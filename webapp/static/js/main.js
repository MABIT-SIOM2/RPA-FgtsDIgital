let allCompanies = [];
let groups = [];
let currentGroup = 'all';
let currentPage = 1;
let itemsPerPage = 10;

// Elementos do DOM (Serão inicializados no DOMContentLoaded)
let companyTbody, groupList, searchInput, loadingOverlay, totalCount, pendingCount;

// Modal
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Inicializa elementos do DOM
    companyTbody = document.getElementById('company-tbody');
    groupList = document.getElementById('group-list');
    searchInput = document.getElementById('company-search');
    loadingOverlay = document.getElementById('loading-overlay');
    totalCount = document.getElementById('total-count');
    pendingCount = document.getElementById('pending-count');

    loadCompanies();
    loadGroups();
    setupGlobalEvents();
});

async function loadCompanies() {
    showLoading(true);
    try {
        const response = await fetch('/api/companies');
        allCompanies = await response.json();
        updateStats();
        filterAndDisplay();
    } catch (error) {
        console.error('Erro ao carregar empresas:', error);
    } finally {
        showLoading(false);
    }
}

async function loadGroups() {
    try {
        const response = await fetch('/api/groups');
        groups = await response.json();
        renderGroupList();
    } catch (error) {
        console.error('Erro ao carregar grupos:', error);
    }
}

function renderGroupList() {
    // Mantém o item "Todas as Carteiras"
    const staticItems = `<li class="${currentGroup === 'all' ? 'active' : ''}" data-group="all">
        <i data-lucide="layers"></i>
        <span>Todas as Carteiras</span>
    </li>`;

    const dynamicItems = groups.map(group => `
        <li class="${currentGroup === group ? 'active' : ''}" data-group="${group}">
            <i data-lucide="folder"></i>
            <span>${group}</span>
        </li>
    `).join('');

    groupList.innerHTML = staticItems + dynamicItems;
    lucide.createIcons();

    // Adiciona eventos de clique
    groupList.querySelectorAll('li').forEach(li => {
        li.addEventListener('click', () => {
            currentGroup = li.getAttribute('data-group');
            currentPage = 1; // Reset to first page
            groupList.querySelectorAll('li').forEach(item => item.classList.remove('active'));
            li.classList.add('active');
            filterAndDisplay();
        });
    });
}

function filterAndDisplay() {
    if (!searchInput) return;

    const searchTerm = searchInput.value.toLowerCase().trim();
    // Normaliza termo de busca para CNPJ (remove caracteres não numéricos)
    const searchTermDigits = searchTerm.replace(/\D/g, '');

    const filtered = allCompanies.filter(company => {
        const matchesGroup = currentGroup === 'all' || company.carteira === currentGroup;
        
        // Dados da empresa para comparação
        const razao = (company.razao || "").toLowerCase();
        const cnpj = (company.cnpj || "");
        const cnpjDigits = cnpj.replace(/\D/g, '');

        const matchesSearch = razao.includes(searchTerm) ||
            cnpj.includes(searchTerm) ||
            (searchTermDigits !== '' && cnpjDigits.includes(searchTermDigits));

        return matchesGroup && matchesSearch;
    });

    const totalItems = filtered.length;
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
    const paginatedItems = filtered.slice(startIndex, endIndex);

    renderTable(paginatedItems);
    renderPagination(totalItems, startIndex, endIndex);
}

function formatCurrency(value) {
    if (value === null || value === undefined) return 'R$ 0,00';

    let numValue = 0;
    if (typeof value === 'number') {
        numValue = value;
    } else if (typeof value === 'string') {
        // Se for string, tentamos identificar se é formato BR (com vírgula) ou US (com ponto decimal)
        let s = value.trim();
        if (s.includes(',') && s.includes('.')) {
            // Formato 1.234,56 -> Remove milhar, troca decimal
            numValue = parseFloat(s.replace(/\./g, '').replace(',', '.'));
        } else if (s.includes(',')) {
            // Formato 1234,56 -> Troca decimal
            numValue = parseFloat(s.replace(',', '.'));
        } else {
            // Formato 1234.56 ou "1234" -> Direto
            numValue = parseFloat(s);
        }
    }

    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numValue || 0);
}

// Funções de formatação de DATA
function formatComp(dateVal) {
    if (!dateVal || dateVal === '-') return '-';
    try {
        const date = new Date(dateVal);
        if (isNaN(date.getTime())) return dateVal;
        
        // Usamos getUTC para evitar deslocamentos de fuso horário que mudam o mês
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        const year = date.getUTCFullYear();
        return `${month}/${year}`;
    } catch (e) {
        return dateVal;
    }
}

function formatDateBR(dateVal) {
    if (!dateVal || dateVal === '-') return '-';
    try {
        const date = new Date(dateVal);
        if (isNaN(date.getTime())) return dateVal;
        
        const day = date.getUTCDate().toString().padStart(2, '0');
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        const year = date.getUTCFullYear();
        return `${day}/${month}/${year}`;
    } catch (e) {
        return dateVal;
    }
}

function renderTable(companies) {
    if (companies.length === 0) {
        companyTbody.innerHTML = `<tr><td colspan="15" style="text-align: center; padding: 40px; color: var(--text-muted);">Nenhuma empresa encontrada.</td></tr>`;
        return;
    }

    companyTbody.innerHTML = companies.map(company => {
        let statusClass = 'pending';
        let statusText = 'Pendente';

        const s = parseInt(company.status);
        if (s === 1) {
            statusClass = 'active-status';
            statusText = 'A Consultar';
        } else if (s === 2) {
            statusClass = 'success';
            statusText = 'Concluido';
        } else if (s === 3) {
            statusClass = 'error';
            statusText = 'Erro';
        }


        return `
            <tr>
                <td style="text-align: center;">
                    <input type="checkbox" class="company-checkbox" data-id="${company.empresa_id}" ${company.status === 1 ? 'checked' : ''}>
                </td>

                <td>${company.cnpj}</td>
                <td>${company.razao}</td>
                <td><span class="status-badge" style="background: #f1f5f9; color: var(--text-muted);">${company.carteira || 'N/A'}</span></td>
                <td>${formatComp(company.competenciaFinal)}</td>
                <td>${formatCurrency(company.valorFgts)}</td>
                <td>${formatCurrency(company.valorFgts13)}</td>
                <td>${formatCurrency(company.valorConsignado)}</td>
                <td><strong>${formatCurrency(company.totalBase)}</strong></td>
                <td style="color: var(--primary); font-weight: 500;">${formatCurrency(company.valorGuiaFgts)}</td>
                <td style="color: var(--primary); font-weight: 500;">${formatCurrency(company.valorGuiaFgts13)}</td>
                <td style="color: var(--primary); font-weight: 500;">${formatCurrency(company.valorGuiaConsignado)}</td>
                <td style="color: var(--primary); font-weight: 700;">${formatCurrency(company.totalGuia)}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        ${statusText}
                    </span>
                </td>
                <td>
                    <button class="btn-icon" onclick="openEditModal(${JSON.stringify(company).replace(/"/g, '&quot;')})" title="Editar">
                        <i data-lucide="edit-3"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    lucide.createIcons();
    setupCheckboxListeners();
}

function setupCheckboxListeners() {
    // Apenas para fins estéticos ou de estado local, se necessário.
    // A gravação real agora volta a ser pelo botão "Gravar Seleção".
}

function setupGlobalEvents() {
    // Selecionar Todos
    const selectAll = document.getElementById('select-all-companies');
    if (selectAll) {
        selectAll.addEventListener('change', async (e) => {
            const checked = e.target.checked;
            const visibleCheckboxes = document.querySelectorAll('.company-checkbox');

            // Atualiza visualmente primeiro
            visibleCheckboxes.forEach(cb => {
                const id = parseInt(cb.getAttribute('data-id'));
                const company = allCompanies.find(c => c.empresa_id === id);
                
                // Só permite o toggle visual se não for Concluído (2)
                // Ou se estamos desmarcando algo que estava Ativo (1)
                if (company && company.status != 2) {
                    cb.checked = checked;
                }
            });

            // Coleta IDs para atualizar no banco seguindo a mesma lógica de segurança
            const idsToUpdate = [];
            const targetStatus = checked ? 1 : 0;

            visibleCheckboxes.forEach(cb => {
                const id = parseInt(cb.getAttribute('data-id'));
                const company = allCompanies.find(c => c.empresa_id === id);
                if (!company) return;

                if (checked) {
                    // Marcando todos: Apenas Pendentes (0) ou Erros (3) vão para Ativo (1)
                    if (company.status == 0 || company.status == 3) {
                        idsToUpdate.push(id);
                    }
                } else {
                    // Desmarcando todos: Apenas os que estão Ativos (1) voltam para Pendente (0)
                    if (company.status == 1) {
                        idsToUpdate.push(id);
                    }
                }
            });

            if (idsToUpdate.length > 0) {
                await fetch('/api/batch-toggle-status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: idsToUpdate, status: targetStatus })
                });
            }

            loadCompanies(); 
        });
    }



    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Evento de busca
    searchInput.addEventListener('input', () => {
        currentPage = 1;
        filterAndDisplay();
    });

    // Eventos de Paginação
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            filterAndDisplay();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        // Usa a lógica centralizada de filtragem para contar total de itens filtrados
        const searchTerm = searchInput.value.toLowerCase().trim();
        const searchTermDigits = searchTerm.replace(/\D/g, '');

        const totalFiltered = allCompanies.filter(company => {
            const matchesGroup = currentGroup === 'all' || company.carteira === currentGroup;
            const razao = (company.razao || "").toLowerCase();
            const cnpj = (company.cnpj || "");
            const cnpjDigits = cnpj.replace(/\D/g, '');

            return matchesGroup && (
                razao.includes(searchTerm) || 
                cnpj.includes(searchTerm) || 
                (searchTermDigits !== '' && cnpjDigits.includes(searchTermDigits))
            );
        }).length;

        if (currentPage * itemsPerPage < totalFiltered) {
            currentPage++;
            filterAndDisplay();
        }
    });

    document.getElementById('items-per-page').addEventListener('change', (e) => {
        itemsPerPage = parseInt(e.target.value);
        currentPage = 1;
        filterAndDisplay();
    });

    // Evento de envio do formulário
    editForm.addEventListener('submit', handleUpdate);

    // Evento de upload de planilha
    const dbUploadInput = document.getElementById('db-upload-input');
    if (dbUploadInput) {
        dbUploadInput.addEventListener('change', async (e) => {
            if (e.target.files.length > 0) {
                await uploadDatabase(e.target.files[0]);
                // Limpa o input para permitir selecionar o mesmo arquivo novamente
                e.target.value = '';
            }
        });
    }
}

async function saveBatchStatus() {
    const consultaCheckboxes = document.querySelectorAll('.company-checkbox');
    
    const selConsultaIds = [];
    const unselConsultaIds = [];

    // 1. Identifica apenas o que mudou na tela (Deltas)
    consultaCheckboxes.forEach(cb => {
        const id = parseInt(cb.getAttribute('data-id'));
        const company = allCompanies.find(c => c.empresa_id === id);
        if (!company) return;

        const currentStatus = parseInt(company.status);
        const isChecked = cb.checked;

        if (isChecked && currentStatus !== 1) {
            // Estava 0, 2 ou 3 e foi marcado (quer consultar)
            selConsultaIds.push(id);
        } else if (!isChecked && currentStatus === 1) {
            // Estava marcado (1) e foi desmarcado (desistiu de consultar)
            unselConsultaIds.push(id);
        }
    });

    if (selConsultaIds.length === 0 && unselConsultaIds.length === 0) {
        alert('Nenhuma alteração detectada para salvar.');
        return;
    }

    const btn = document.getElementById('btn-save-batch');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="spinner-small"></i> Gravando...';

    showLoading(true);
    try {
        // Envia atualizações apenas se houver mudanças
        if (selConsultaIds.length > 0) {
            await fetch('/api/batch-toggle-status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: selConsultaIds, status: 1 })
            });
        }
        
        if (unselConsultaIds.length > 0) {
            await fetch('/api/batch-toggle-status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: unselConsultaIds, status: 0 })
            });
        }

        alert(`Sucesso! ${selConsultaIds.length + unselConsultaIds.length} alteração(ões) gravada(s).`);
        await loadCompanies();
    } catch (error) {
        console.error('Erro ao gravar em lote:', error);
        alert('Erro ao gravar as seleções no banco de dados.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        showLoading(false);
    }
}

async function uploadDatabase(file) {
    const formData = new FormData();
    formData.append('file', file);

    showLoading(true);
    try {
        const response = await fetch('/api/upload-database', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            let detailsMsg = "";
            if (result.results && result.results.errors > 0) {
                detailsMsg = "\n\nFalhas identificadas:\n" + result.results.details.slice(0, 5).join('\n');
                if (result.results.details.length > 5) detailsMsg += "\n...";
            }
            alert(result.message + detailsMsg);
            loadCompanies(); // Recarrega a tabela
        } else {
            alert('Erro no processamento: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        alert('Erro ao enviar arquivo para o servidor.');
    } finally {
        showLoading(false);
    }
}

async function updateCompanyStatus(id, status) {
    try {
        await fetch('/api/toggle-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ empresa_id: id, status: status })
        });
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

function updateStats() {
    totalCount.textContent = allCompanies.length;
    pendingCount.textContent = allCompanies.filter(c => c.status == 1).length;
    // O texto da legenda de pendingCount na verdade refere-se a "Prontos para consultar" no contexto do usuário
}

function openEditModal(company) {
    document.getElementById('edit-id').value = company.empresa_id;
    document.getElementById('edit-razao').value = company.razao;
    document.getElementById('edit-cnpj').value = company.cnpj;

    // Novos campos roboFgts (Formatados para exibição amigável)
    document.getElementById('edit-comp-ini').value = formatComp(company.competenciaInicial);
    document.getElementById('edit-comp-fim').value = formatComp(company.competenciaFinal);
    document.getElementById('edit-base-fgts').value = company.valorFgts || 0;
    document.getElementById('edit-base-fgts13').value = company.valorFgts13 || 0;
    document.getElementById('edit-base-consignado').value = company.valorConsignado || 0;
    document.getElementById('edit-base-total').value = company.totalBase || 0;

    document.getElementById('edit-fgts').value = company.valorGuiaFgts || 0;
    document.getElementById('edit-fgts13').value = company.valorGuiaFgts13 || 0;
    document.getElementById('edit-consignado').value = company.valorGuiaConsignado || 0;
    document.getElementById('edit-total').value = company.totalGuia || 0;

    editModal.classList.remove('hidden');
}

function closeModal() {
    editModal.classList.add('hidden');
    editForm.reset();
}

async function handleUpdate(e) {
    e.preventDefault();

    const data = {
        empresa_id: document.getElementById('edit-id').value,
        competenciaInicial: document.getElementById('edit-comp-ini').value,
        competenciaFinal: document.getElementById('edit-comp-fim').value,
        valorFgts: document.getElementById('edit-base-fgts').value,
        valorFgts13: document.getElementById('edit-base-fgts13').value,
        valorConsignado: document.getElementById('edit-base-consignado').value,
        totalBase: document.getElementById('edit-base-total').value,
        // As colunas de extração (Guia) são excluídas daqui pois são preenchidas apenas pelo robô
    };

    const submitBtn = editForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Salvando...';

    try {
        const response = await fetch('/api/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            closeModal();
            loadCompanies(); // Recarrega para ver a mudança
        } else {
            alert('Erro: ' + (result.message || 'Falha ao salvar.'));
        }
    } catch (error) {
        console.error('Erro ao atualizar:', error);
        alert('Erro de conexão com o servidor.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

function showLoading(show) {
    if (show) loadingOverlay.classList.remove('hidden');
    else loadingOverlay.classList.add('hidden');
}

async function exportReport() {
    const btn = document.getElementById('btn-export-report');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="spinner-small"></i> Exportando...';

    try {
        let exportUrl = '/api/export';
        if (currentGroup && currentGroup !== 'all') {
            exportUrl += `?group=${encodeURIComponent(currentGroup)}`;
        }
        const response = await fetch(exportUrl);

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.message || 'Erro ao exportar relatório');
        }

        // Recebe o blob do arquivo
        const blob = await response.blob();

        // Extrai o nome do arquivo do header Content-Disposition se disponível
        let filename = 'Relatorio_FGTS.xlsx';
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('filename=') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // Cria um link temporário para download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Limpeza
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Erro ao exportar:', error);
        alert('Erro ao exportar: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}

async function exportPDF() {
    const btn = document.getElementById('btn-export-pdf');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="spinner-small"></i> Exportando...';

    try {
        let exportUrl = '/api/export-pdf';
        if (currentGroup && currentGroup !== 'all') {
            exportUrl += `?group=${encodeURIComponent(currentGroup)}`;
        }
        const response = await fetch(exportUrl);

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.message || 'Erro ao exportar PDF');
        }

        const blob = await response.blob();
        let filename = 'Relatorio_FGTS.pdf';
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('filename=') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Erro ao exportar PDF:', error);
        alert('Erro ao exportar PDF: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}

function renderPagination(totalItems, start, end) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // Atualiza info
    document.getElementById('pagination-start').textContent = totalItems > 0 ? start + 1 : 0;
    document.getElementById('pagination-end').textContent = end;
    document.getElementById('pagination-total-items').textContent = totalItems;

    // Atualiza botões
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;

    // Renderiza números de página
    const pageNumbers = document.getElementById('page-numbers');
    let html = '';

    // Mostra no máximo 5 botões de página
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);

    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="page-num ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }

    pageNumbers.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    filterAndDisplay();
}
