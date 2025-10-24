document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    if (!table) return; // إذا ما فيه جدول، لا نفعل أي شيء

    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");

    // وظيفة الفلترة وترقيم الصفوف
    function filterTable() {
        const selectedClass = classSelect ? classSelect.value : '';
        const selectedSection = sectionSelect ? sectionSelect.value : '';
        let visibleIndex = 1; // لترقيم الصفوف المرئية فقط

        table.querySelectorAll("tbody tr").forEach(row => {
            let show = true;

            // فلترة حسب الصف والشعبة
            if (selectedClass && row.dataset.class !== selectedClass) show = false;
            if (selectedSection && row.dataset.section !== selectedSection) show = false;

            row.style.display = show ? "" : "none";

            // تحديث الترقيم فقط للصفوف المرئية
            if (show) {
                const numberCell = row.querySelector(".row-number");
                if (numberCell) numberCell.textContent = visibleIndex++;
            }
        });
    }

    // تفعيل الفلترة عند تغيير الصف أو الشعبة
    if (classSelect) classSelect.addEventListener("change", filterTable);
    if (sectionSelect) sectionSelect.addEventListener("change", filterTable);

    // تحديث الحضور/الملاحظة عند تغيير أي checkbox
    table.addEventListener("change", (e) => {
        const cb = e.target;
        if (!cb.classList.contains("attendance-checkbox")) return;

        const studentId = cb.dataset.studentId;
        const status = cb.dataset.status;

        // التأكد أن حالة الحضور متناقضة مع البقية في نفس الصف
        const row = cb.closest("tr");
        row.querySelectorAll(".attendance-checkbox").forEach(otherCb => {
            if (otherCb !== cb) otherCb.checked = false;
        });

        // إرسال البيانات إلى السيرفر
        fetch("/tracking/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: studentId, note: status })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) alert("حدث خطأ أثناء حفظ الملاحظة");
        })
        .catch(() => alert("تعذر الاتصال بالخادم"));
    });

    // ترقيم الصفوف عند التحميل الأول
    filterTable();
});
