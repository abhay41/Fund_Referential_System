const API_BASE = (window.API_BASE) ? window.API_BASE : 'http://localhost:8000';

async function fetchFunds(page = 1, pageSize = 10) {
  const skip = (page - 1) * pageSize;
  const resp = await fetch(`${API_BASE}/funds/?skip=${skip}&limit=${pageSize}`);
  if (!resp.ok) throw new Error('Failed to fetch funds');
  return resp.json();
}

async function fetchManagementEntities(limit = 50) {
  const resp = await fetch(`${API_BASE}/management/?skip=0&limit=${limit}`);
  if (!resp.ok) throw new Error('Failed to fetch management entities');
  return resp.json();
}

function renderFunds(fundsData) {
  const container = document.getElementById('funds-list');
  container.innerHTML = '';
  fundsData.forEach(f => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-start';
    item.innerHTML = `
      <div>
        <div class="fw-bold">${f.fund_name || f.fund_code || f.id || f.fund_id}</div>
        <div class="small text-muted">Fund ID: ${f.fund_id || f.id}</div>
      </div>
      <div class="text-end">
        <small class="text-muted">${f.fund_type || ''}</small>
        <div class="text-muted">${f.management_entity ? f.management_entity.mgmt_id || f.management_entity.id : '—'}</div>
      </div>
    `;
    item.addEventListener('click', () => showFundDetail(f.fund_id || f.id));
    container.appendChild(item);
  });
}

function renderManagement(entities) {
  const container = document.getElementById('management-list');
  container.innerHTML = '';
  entities.forEach(e => {
    const node = document.createElement('div');
    node.className = 'list-group-item';
    node.textContent = `${e.mgmt_id || e.id} — ${e.registration_no || ''}`;
    container.appendChild(node);
  });
}

async function showFundDetail(fundId) {
  const resp = await fetch(`${API_BASE}/funds/${encodeURIComponent(fundId)}`);
  if (!resp.ok) {
    alert('Could not fetch fund details');
    return;
  }
  const fund = await resp.json();
  const body = document.getElementById('fund-detail-body');
  body.innerHTML = `
    <h5>${fund.fund_name || fund.fund_code}</h5>
    <p><strong>Fund ID:</strong> ${fund.fund_id || fund.id}</p>
    <p><strong>Type:</strong> ${fund.fund_type || ''} — <strong>Status:</strong> ${fund.status || ''}</p>
    <h6>Management Entity</h6>
    <pre>${JSON.stringify(fund.management_entity, null, 2)}</pre>
    <h6>Legal Entity</h6>
    <pre>${JSON.stringify(fund.legal_entity, null, 2)}</pre>
    <h6>Share Classes</h6>
    <pre>${JSON.stringify(fund.share_classes, null, 2)}</pre>
    <h6>Subfunds</h6>
    <pre>${JSON.stringify(fund.subfunds, null, 2)}</pre>
  `;
  const modalEl = document.getElementById('fundModal');
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// Pagination render
function renderPagination(total, pageSize, currentPage) {
  const pages = Math.ceil(total / pageSize);
  const ul = document.getElementById('funds-pagination');
  ul.innerHTML = '';
  for (let i = 1; i <= pages; i++) {
    const li = document.createElement('li');
    li.className = 'page-item' + (i === currentPage ? ' active' : '');
    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = '#';
    a.textContent = i;
    a.addEventListener('click', (e) => { e.preventDefault(); loadFunds(i); });
    li.appendChild(a);
    ul.appendChild(li);
  }
}

async function loadFunds(page = 1) {
  try {
    const pageSize = 10;
    const result = await fetchFunds(page, pageSize);
    if (result.data) {
      renderFunds(result.data);
      renderPagination(result.total, pageSize, page);
    } else {
      // older endpoints return array
      renderFunds(result);
    }
  } catch (err) {
    console.error(err);
    document.getElementById('funds-list').textContent = 'Failed to load funds.';
  }
}

async function loadManagement() {
  try {
    const ents = await fetchManagementEntities(100);
    renderManagement(ents);
  } catch (err) {
    console.error(err);
    document.getElementById('management-list').textContent = 'Failed to load management entities.';
  }
}

// Initialize
loadFunds(1);
loadManagement();
