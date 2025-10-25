document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    if (!table) return;

    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");

    function filterTable() {
        const selectedClass = classSelect ? classSelect.value : '';
        const selectedSection = sectionSelect ? sectionSelect.value : '';
        let visibleIndex = 1;

        table.querySelectorAll("tbody tr").forEach(row => {
            let show = true;
            if (selectedClass && row.dataset.class !== selectedClass) show = false;
            if (selectedSection && row.dataset.section !== selectedSection) show = false;

            row.style.display = show ? "" : "none";

            if (show) {
                const numberCell = row.querySelector(".row-number");
                if (numberCell) numberCell.textContent = visibleIndex++;
            }
        });
    }

    if (classSelect) classSelect.addEventListener("change", filterTable);
    if (sectionSelect) sectionSelect.addEventListener("change", filterTable);

    table.addEventListener("change", (e) => {
        const cb = e.target;
        if (!cb.classList.contains("attendance-checkbox")) return;

        const row = cb.closest("tr");
        const studentId = cb.dataset.studentId;
        const status = cb.dataset.status;
        const schoolId = row.dataset.school;
        const teacherId = row.dataset.teacher;
        const dateVal = row.dataset.date;
        const note = status;

        // التأكد من التحقق المتبادل بين checkboxes في نفس الصف
        row.querySelectorAll(".attendance-checkbox").forEach(otherCb => {
            if (otherCb !== cb) otherCb.checked = false;
        });

        // إرسال البيانات إلى الراوت الصحيح للـ blueprint
        fetch("/attendance/update_attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: studentId,
                status: status,
                school_id: schoolId,
                teacher_id: teacherId,
                date: dateVal,
                note: note
            })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) alert("حدث خطأ أثناء حفظ الملاحظة");
        })
        .catch(() => alert("تعذر الاتصال بالخادم"));
    });

    // ترقيم الصفوف عند التحميل
    filterTable();
});
