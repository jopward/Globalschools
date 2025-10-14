document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("subjectForm");
  const editForm = document.getElementById("editForm");
  const tableBody = document.getElementById("subjectsBody");
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));

  // تحميل المواد عند فتح الصفحة
  fetchSubjects();

  // إضافة مادة جديدة
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = {
      name: form.name.value.trim(),
      code: form.code.value.trim(),
      description: form.description.value.trim(),
    };

    if (!formData.name) return alert("يرجى إدخال اسم المادة");

    try {
      const res = await fetch("/subjects/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        alert("✅ تمت إضافة المادة بنجاح");
        form.reset();
        fetchSubjects();
      } else {
        const data = await res.json();
        alert("❌ خطأ: " + (data.error || "حدث خطأ"));
      }
    } catch (err) {
      console.error(err);
      alert("فشل الاتصال بالخادم");
    }
  });

  // جلب المواد
  async function fetchSubjects() {
    try {
      const res = await fetch("/subjects/");
      const data = await res.json();
      tableBody.innerHTML = "";

      if (!data.length) {
        tableBody.innerHTML = `<tr><td colspan="5">لا توجد مواد</td></tr>`;
        return;
      }

      data.forEach((subj, i) => {
        const row = `
          <tr>
            <td>${i + 1}</td>
            <td>${subj.name}</td>
            <td>${subj.code || "-"}</td>
            <td>${subj.description || "-"}</td>
            <td>
              <button class="btn btn-sm btn-warning me-2" onclick="editSubject(${subj.id}, '${subj.name}', '${subj.code || ""}', '${subj.description || ""}')">تعديل</button>
              <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subj.id})">حذف</button>
            </td>
          </tr>`;
        tableBody.insertAdjacentHTML("beforeend", row);
      });
    } catch (err) {
      console.error(err);
    }
  }

  // تعديل المادة
  window.editSubject = (id, name, code, description) => {
    document.getElementById("edit_id").value = id;
    document.getElementById("edit_name").value = name;
    document.getElementById("edit_code").value = code;
    document.getElementById("edit_description").value = description;
    editModal.show();
  };

  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("edit_id").value;
    const formData = {
      name: document.getElementById("edit_name").value.trim(),
      code: document.getElementById("edit_code").value.trim(),
      description: document.getElementById("edit_description").value.trim(),
    };

    try {
      const res = await fetch(`/subjects/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        alert("✅ تم تعديل المادة بنجاح");
        editModal.hide();
        fetchSubjects();
      } else {
        alert("❌ فشل في تعديل المادة");
      }
    } catch (err) {
      console.error(err);
    }
  });

  // حذف المادة
  window.deleteSubject = async (id) => {
    if (!confirm("هل أنت متأكد من حذف هذه المادة؟")) return;

    try {
      const res = await fetch(`/subjects/${id}`, { method: "DELETE" });
      if (res.ok) {
        alert("🗑️ تم حذف المادة بنجاح");
        fetchSubjects();
      } else {
        alert("❌ فشل في الحذف");
      }
    } catch (err) {
      console.error(err);
    }
  };
});
