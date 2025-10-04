// static/js/crud.js
document.addEventListener('DOMContentLoaded', () => {
  const API_BASE = window.API_SCHOOLS || '/schools';

  const tbody = document.getElementById('schoolsTableBody');
  const modalEl = document.getElementById('modalForm');
  const modalForm = document.getElementById('modalFormElement');
  const modal = new bootstrap.Modal(modalEl);
  const submitBtn = document.getElementById('modalSubmitBtn');
  const submitText = document.getElementById('modalSubmitText');
  const modalSpinner = document.getElementById('modalSpinner');
  const formAlert = document.getElementById('formAlert');
  const toggleAdminPw = document.getElementById('toggleAdminPw');

  const deleteModalEl = document.getElementById('modalDelete');
  const deleteModal = new bootstrap.Modal(deleteModalEl);
  const deleteSchoolName = document.getElementById('deleteSchoolName');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  const deleteSpinner = document.getElementById('deleteSpinner');
  const deleteAlert = document.getElementById('deleteAlert');

  function showToast(message, type = 'success') {
    const id = `t${Date.now()}`;
    const toastHtml = `
      <div id="${id}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="إغلاق"></button>
        </div>
      </div>`;
    const container = document.getElementById('toastsContainer');
    container.insertAdjacentHTML('beforeend', toastHtml);
    const tEl = document.getElementById(id);
    new bootstrap.Toast(tEl, { delay: 4000 }).show();
    tEl.addEventListener('hidden.bs.toast', () => tEl.remove());
  }

  if (toggleAdminPw) {
    toggleAdminPw.addEventListener('click', () => {
      const pw = document.getElementById('admin_password');
      if (!pw) return;
      const type = pw.type === 'password' ? 'text' : 'password';
      pw.type = type;
      toggleAdminPw.textContent = type === 'password' ? 'إظهار' : 'إخفاء';
    });
  }

  document.querySelectorAll('[data-bs-target="#modalForm"]').forEach(btn => {
    btn.addEventListener('click', () => {
      modalForm.reset();
      modalForm.classList.remove('was-validated');
      formAlert.classList.add('d-none');
      document.getElementById('school_id').value = '';
      submitText.textContent = 'إضافة';
      modalForm.dataset.mode = 'add';
      setTimeout(() => document.getElementById('school_name').focus(), 200);
    });
  });

  tbody && tbody.addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-btn');
    const deleteBtn = e.target.closest('.delete-btn');
    const tr = e.target.closest('tr');
    if (!tr) return;

    const schoolId = tr.dataset.id || tr.getAttribute('data-id');

    if (editBtn) {
      const name = tr.querySelector('.school-name')?.textContent?.trim() || '';
      const admin = tr.querySelector('.admin-username')?.textContent?.trim() || '';
      document.getElementById('school_id').value = schoolId;
      document.getElementById('school_name').value = name;
      document.getElementById('admin_username').value = admin;
      document.getElementById('admin_password').value = '';
      submitText.textContent = 'حفظ التغييرات';
      modalForm.dataset.mode = 'edit';
      modal.show();
      setTimeout(() => document.getElementById('school_name').focus(), 200);
      return;
    }

    if (deleteBtn) {
      const name = tr.querySelector('.school-name')?.textContent?.trim() || '';
      deleteSchoolName.textContent = name;
      confirmDeleteBtn.dataset.schoolId = schoolId;
      deleteAlert.classList.add('d-none');
      deleteModal.show();
      return;
    }
  });

  modalForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    modalForm.classList.add('was-validated');
    if (!modalForm.checkValidity()) return;

    const mode = modalForm.dataset.mode || 'add';
    const id = document.getElementById('school_id').value;
    const payload = {
      school_name: document.getElementById('school_name').value.trim(),
      admin_username: document.getElementById('admin_username').value.trim(),
      admin_password: document.getElementById('admin_password').value
    };

    submitBtn.disabled = true;
    modalSpinner.classList.remove('d-none');
    formAlert.classList.add('d-none');

    try {
      const url = mode === 'add' ? API_BASE : `${API_BASE}/${id}`;
      const method = mode === 'add' ? 'POST' : 'PUT';
      const res = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      const data = await res.json().catch(()=>({}));

      if (!res.ok) {
        const msg = data.error || data.message || 'فشل الطلب';
        formAlert.className = 'alert alert-danger';
        formAlert.textContent = msg;
        formAlert.classList.remove('d-none');
        throw new Error(msg);
      }

      if (mode === 'add') {
        const newId = data.school_id || Date.now();
        const row = document.createElement('tr');
        row.setAttribute('data-id', newId);
        const index = tbody.children.length + 1;
        row.innerHTML = `
          <td>${index}</td>
          <td class="school-name">${payload.school_name}</td>
          <td class="admin-username">${payload.admin_username}</td>
          <td class="table-actions">
            <i class="bi bi-pencil-square text-primary edit-btn" title="تعديل"></i>
            <i class="bi bi-trash text-danger delete-btn" title="حذف"></i>
          </td>
        `;
        tbody.appendChild(row);
        showToast(data.message || 'تمت الإضافة');
      } else {
        const row = tbody.querySelector(`tr[data-id="${id}"]`);
        if (row) {
          row.querySelector('.school-name').textContent = payload.school_name;
          row.querySelector('.admin-username').textContent = payload.admin_username;
        }
        showToast(data.message || 'تم التحديث');
      }

      modal.hide();
      modalForm.reset();
    } catch (err) {
      console.error(err);
      if (!formAlert.classList.contains('d-none')) {} 
      else showToast('حدث خطأ، تحقق من الاتصال', 'danger');
    } finally {
      submitBtn.disabled = false;
      modalSpinner.classList.add('d-none');
    }
  });

  confirmDeleteBtn && confirmDeleteBtn.addEventListener('click', async () => {
    const id = confirmDeleteBtn.dataset.schoolId;
    if (!id) return;
    confirmDeleteBtn.disabled = true;
    deleteSpinner.classList.remove('d-none');
    deleteAlert.classList.add('d-none');

    try {
      const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
      const data = await res.json().catch(()=>({}));

      if (!res.ok) {
        deleteAlert.className = 'alert alert-danger';
        deleteAlert.textContent = data.error || data.message || 'فشل الحذف';
        deleteAlert.classList.remove('d-none');
        throw new Error('delete failed');
      }

      const row = tbody.querySelector(`tr[data-id="${id}"]`);
      if (row) row.remove();
      Array.from(tbody.children).forEach((r, idx) => r.children[0].innerText = idx + 1);

      deleteModal.hide();
      showToast(data.message || 'تم حذف المدرسة والمديرين بنجاح', 'success');
    } catch (err) {
      console.error(err);
      showToast('فشل الحذف', 'danger');
    } finally {
      confirmDeleteBtn.disabled = false;
      deleteSpinner.classList.add('d-none');
    }
  });

});
