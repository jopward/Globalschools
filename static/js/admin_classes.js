document.addEventListener("DOMContentLoaded", () => {
  const addClassBtn = document.getElementById("addClassBtn");
  const classNameInput = document.getElementById("classNameInput");
  const sectionInput = document.getElementById("sectionInput");
  const periodSelect = document.getElementById("periodSelect");
  const classesTableBody = document.getElementById("classesTableBody");

  // --- تحميل الصفوف عند فتح الصفحة ---
  fetchClasses();

  // --- حدث إضافة صف ---
  addClassBtn.addEventListener("click", async () => {
    const className = classNameInput.value.trim();
    const section = sectionInput.value.trim();
    const period = periodSelect.value;

    if (!className) {
      alert("الرجاء إدخال اسم الصف");
      return;
    }

    try {
      const response = await fetch(window.API_CLASSES, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ class_name: className, section: section, period: period })
      });

      const data = await response.json();
      if (response.ok) {
        // أضف الصف للجدول مباشرة
        addClassRow({ id: data.class_id, class_name: className, section, period });
        classNameInput.value = "";
        sectionInput.value = "";
        periodSelect.value = "صباحي";
      } else {
        alert(data.error || "حدث خطأ أثناء الإضافة");
      }
    } catch (err) {
      console.error(err);
      alert("فشل الاتصال بالخادم");
    }
  });

  // --- تحميل كل الصفوف ---
  async function fetchClasses() {
    try {
      const response = await fetch(window.API_CLASSES);
      const classes = await response.json();
      classesTableBody.innerHTML = "";
      classes.forEach(cls => addClassRow(cls));
    } catch (err) {
      console.error(err);
      alert("فشل تحميل الصفوف");
    }
  }

  // --- إضافة صف جديد للجدول ---
  function addClassRow(cls) {
    const tr = document.createElement("tr");
    tr.dataset.id = cls.id;

    tr.innerHTML = `
      <td>${classesTableBody.children.length + 1}</td>
      <td class="class-name">${cls.class_name}</td>
      <td class="section-name">${cls.section || "غير محدد"}</td>
      <td class="period">${cls.period}</td>
      <td class="table-actions">
        <i class="bi bi-pencil-square text-primary edit-btn" title="تعديل"></i>
        <i class="bi bi-trash text-danger delete-btn" title="حذف"></i>
      </td>
    `;
    classesTableBody.appendChild(tr);

    // إضافة أحداث تعديل وحذف
    const editBtn = tr.querySelector(".edit-btn");
    const deleteBtn = tr.querySelector(".delete-btn");

    editBtn.addEventListener("click", () => editClass(tr));
    deleteBtn.addEventListener("click", () => deleteClass(tr));
  }

  // --- تعديل صف ---
  async function editClass(tr) {
    const classId = tr.dataset.id;
    const className = prompt("أدخل اسم الصف الجديد:", tr.querySelector(".class-name").textContent);
    if (className === null) return;
    const section = prompt("أدخل الشعبة الجديدة:", tr.querySelector(".section-name").textContent);
    if (section === null) return;
    const period = prompt("أدخل الفترة (صباحي/مسائي):", tr.querySelector(".period").textContent);
    if (period === null) return;

    try {
      const response = await fetch(`${window.API_CLASSES}/${classId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ class_name: className, section, period })
      });
      const data = await response.json();
      if (response.ok) {
        tr.querySelector(".class-name").textContent = className;
        tr.querySelector(".section-name").textContent = section;
        tr.querySelector(".period").textContent = period;
      } else {
        alert(data.error || "فشل التحديث");
      }
    } catch (err) {
      console.error(err);
      alert("فشل الاتصال بالخادم");
    }
  }

  // --- حذف صف ---
  async function deleteClass(tr) {
    const classId = tr.dataset.id;
    if (!confirm("هل أنت متأكد من حذف هذا الصف؟")) return;

    try {
      const response = await fetch(`${window.API_CLASSES}/${classId}`, { method: "DELETE" });
      const data = await response.json();
      if (response.ok) {
        tr.remove();
        // إعادة ترقيم الصفوف
        Array.from(classesTableBody.children).forEach((row, idx) => {
          row.firstElementChild.textContent = idx + 1;
        });
      } else {
        alert(data.error || "فشل الحذف");
      }
    } catch (err) {
      console.error(err);
      alert("فشل الاتصال بالخادم");
    }
  }
});
