document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    if (!table) return;

    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");

    // تخزين حالة الشيك بوكسات حتى بعد التصفية
    const attendanceState = {};

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

            // إعادة ضبط الشيك بوكسات حسب الحالة المخزنة
            row.querySelectorAll(".attendance-checkbox").forEach(cb => {
                const key = cb.dataset.studentId + "_" + cb.dataset.status;
                cb.checked = attendanceState[key] ? true : false;
            });
        });
    }

    if (classSelect) classSelect.addEventListener("change", filterTable);
    if (sectionSelect) sectionSelect.addEventListener("change", filterTable);

    // =============================
    // عند تغيير الشيك بوكس
    // =============================
    table.addEventListener("change", (e) => {
        const cb = e.target;
        if (!cb.classList.contains("attendance-checkbox")) return;

        const row = cb.closest("tr");
        const studentId = cb.dataset.studentId;
        const status = cb.dataset.status;
        const schoolId = row.dataset.school;
        const teacherId = row.dataset.teacher;
        const dateVal = row.dataset.date || new Date().toISOString().split("T")[0];
        const note = status;
        const trackingId = cb.dataset.trackingId || null;
        const key = studentId + "_" + status;

        // التأكد من اختيار واحد فقط في الصف
        row.querySelectorAll(".attendance-checkbox").forEach(otherCb => {
            if (otherCb !== cb) otherCb.checked = false;
        });

        // =============================
        // إذا تم التحديد ✅
        // =============================
        if (cb.checked) {
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
                if (data.success) {
                    cb.dataset.trackingId = data.tracking_id || ""; // حفظ ID السجل الجديد
                    attendanceState[key] = true; // حفظ الحالة محليًا
                } else {
                    alert(data.error || "حدث خطأ أثناء حفظ الحضور");
                    cb.checked = false;
                }
            })
            .catch(() => {
                alert("تعذر الاتصال بالخادم");
                cb.checked = false;
            });
        } 
        // =============================
        // إذا ألغى التحديد ❌
        // =============================
        else {
            if (!trackingId) {
                delete attendanceState[key];
                return;
            }

            fetch("/attendance/delete_attendance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tracking_id: trackingId })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    alert(data.error || "حدث خطأ أثناء حذف السجل");
                } else {
                    cb.dataset.trackingId = "";
                    delete attendanceState[key];
                }
            })
            .catch(() => alert("تعذر الاتصال بالخادم"));
        }
    });

    // ترقيم الصفوف عند التحميل
    filterTable();
});
