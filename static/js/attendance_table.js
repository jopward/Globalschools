document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    if (!table) return;

    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");
    const dateSelect = document.getElementById("dateSelect");
    const attendanceState = {}; // لتخزين حالة الشيك بوكسات

    // =============================
    // فلترة حسب الصف والشعبة
    // =============================
    function filterTable() {
        const selectedClass = classSelect ? classSelect.value : '';
        const selectedSection = sectionSelect ? sectionSelect.value : '';
        let visibleIndex = 1;

        table.querySelectorAll("tbody tr").forEach(row => {
            const rowClass = row.dataset.class;
            const rowSection = row.dataset.section;

            const matchClass = !selectedClass || rowClass === selectedClass;
            const matchSection = !selectedSection || rowSection === selectedSection;

            const visible = matchClass && matchSection;
            row.style.display = visible ? "" : "none";

            if (visible) {
                const numberCell = row.querySelector(".row-number");
                if (numberCell) numberCell.textContent = visibleIndex++;
            }
        });
    }

    if (classSelect) classSelect.addEventListener("change", filterTable);
    if (sectionSelect) sectionSelect.addEventListener("change", filterTable);

    // =============================
    // تحميل بيانات التاريخ المختار
    // =============================
    if (dateSelect) {
        dateSelect.addEventListener("change", () => {
            const selectedDate = dateSelect.value;
            fetch(`/attendance/filter?date=${selectedDate}`)
                .then(res => res.json())
                .then(data => {
                    // مسح كل الشيك بوكسات
                    document.querySelectorAll(".attendance-checkbox").forEach(cb => {
                        cb.checked = false;
                        cb.dataset.trackingId = "";
                    });

                    // إعادة تعيين القيم من قاعدة البيانات
                    data.forEach(row => {
                        const cb = document.querySelector(
                            `.attendance-checkbox[data-student-id="${row.student_id}"][data-status="${row.attendance}"]`
                        );
                        if (cb) {
                            cb.checked = true;
                            cb.dataset.trackingId = row.id;
                        }
                    });
                })
                .catch(() => alert("❌ خطأ أثناء تحميل بيانات التاريخ"));
        });
    }

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
        const dateVal = dateSelect ? dateSelect.value : new Date().toISOString().split("T")[0];
        const note = status;
        const trackingId = cb.dataset.trackingId || null;
        const key = studentId + "_" + status;

        // تأكد أن صف واحد فقط محدد
        row.querySelectorAll(".attendance-checkbox").forEach(otherCb => {
            if (otherCb !== cb) otherCb.checked = false;
        });

        if (cb.checked) {
            fetch("/attendance/update", {
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
                        cb.dataset.trackingId = data.tracking_id || "";
                        attendanceState[key] = true;
                    } else {
                        alert(data.error || "حدث خطأ أثناء الحفظ");
                        cb.checked = false;
                    }
                })
                .catch(() => {
                    alert("تعذر الاتصال بالخادم");
                    cb.checked = false;
                });
        } else {
            if (!trackingId) {
                delete attendanceState[key];
                return;
            }

            fetch("/attendance/delete", {
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

    // =============================
    // تحديث تلقائي بعد منتصف الليل ⏰
    // =============================
    function checkMidnightRefresh() {
        const now = new Date();
        if (now.getHours() === 0 && now.getMinutes() === 0) {
            console.log("⏰ منتصف الليل - تحديث الصفحة...");
            window.location.reload();
        }
    }

    // فحص كل دقيقة
    setInterval(checkMidnightRefresh, 60000);

    // ترقيم الصفوف
    filterTable();
});
