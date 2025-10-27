document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    const attendanceBody = document.getElementById("attendanceBody");
    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");
    const dateInput = document.getElementById("attendanceDate");

    if (!table || !dateInput) return;

    // =============================
    // 🧠 تخزين مؤقت لحالة الشيك بوكسات
    // =============================
    const attendanceState = {};

    // =============================
    // 🗓️ تحميل بيانات اليوم عند الفتح أو عند تغيير التاريخ
    // =============================
    async function loadAttendanceByDate(selectedDate) {
        try {
            const res = await fetch(`/attendance/filter?date=${selectedDate}`);
            if (!res.ok) throw new Error("خطأ في تحميل بيانات الحضور");
            const data = await res.json();

            // تفريغ جميع الشيك بوكسات أولاً
            attendanceBody.querySelectorAll(".attendance-checkbox").forEach(cb => {
                cb.checked = false;
                cb.dataset.trackingId = "";
            });

            // تطبيق البيانات القادمة من الخادم
            data.forEach(rec => {
                const row = attendanceBody.querySelector(`[data-student-id-row='${rec.student_id}']`);
                if (!row) return;

                const cb = row.querySelector(`.attendance-checkbox[data-status='${rec.attendance}']`);
                if (cb) {
                    cb.checked = true;
                    cb.dataset.trackingId = rec.id;
                    attendanceState[rec.student_id + "_" + rec.attendance] = true;
                }
            });

            console.log(`✅ تم تحميل بيانات الحضور لتاريخ ${selectedDate}`);
        } catch (err) {
            console.error("❌ خطأ أثناء تحميل الحضور:", err);
            alert("حدث خطأ أثناء تحميل بيانات الحضور");
        }
    }

    // =============================
    // 📅 تغيير التاريخ
    // =============================
    dateInput.addEventListener("change", () => {
        const newDate = dateInput.value;
        if (!newDate) return;

        // تحديث بيانات التاريخ في الصفوف
        attendanceBody.querySelectorAll("tr").forEach(row => {
            row.dataset.date = newDate;
        });

        // تحميل البيانات الخاصة بهذا التاريخ
        loadAttendanceByDate(newDate);
    });

    // =============================
    // 📋 فلترة الجدول حسب الصف والشعبة
    // =============================
    function filterTable() {
        const selectedClass = classSelect ? classSelect.value : '';
        const selectedSection = sectionSelect ? sectionSelect.value : '';
        let visibleIndex = 1;

        attendanceBody.querySelectorAll("tr").forEach(row => {
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

    // =============================
    // ✅ التعامل مع الشيك بوكس (إضافة / تحديث / حذف)
    // =============================
    attendanceBody.addEventListener("change", async (e) => {
        const cb = e.target;
        if (!cb.classList.contains("attendance-checkbox")) return;

        const row = cb.closest("tr");
        const studentId = cb.dataset.studentId;
        const status = cb.dataset.status;
        const schoolId = row.dataset.school;
        const teacherId = row.dataset.teacher;
        const dateVal = row.dataset.date || dateInput.value;
        const note = status;
        const trackingId = cb.dataset.trackingId || null;
        const key = `${studentId}_${status}`;

        // إلغاء باقي الشيك بوكسات الصف نفسه
        row.querySelectorAll(".attendance-checkbox").forEach(otherCb => {
            if (otherCb !== cb) otherCb.checked = false;
        });

        try {
            // ✅ إذا ضغط المعلم على شيك بوكس
            if (cb.checked) {
                const res = await fetch("/attendance/update", {
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
                });
                const data = await res.json();

                if (data.success) {
                    cb.dataset.trackingId = data.tracking_id;
                    attendanceState[key] = true;
                } else {
                    alert(data.error || "حدث خطأ أثناء حفظ الحضور");
                    cb.checked = false;
                }
            } 
            // ❌ إذا شال الصح
            else {
                if (!trackingId) {
                    delete attendanceState[key];
                    return;
                }

                const res = await fetch("/attendance/delete", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tracking_id: trackingId })
                });
                const data = await res.json();

                if (data.success) {
                    cb.dataset.trackingId = "";
                    delete attendanceState[key];
                } else {
                    alert(data.error || "حدث خطأ أثناء حذف السجل");
                }
            }
        } catch (err) {
            console.error("❌ خطأ أثناء تحديث الحضور:", err);
            alert("حدث خطأ في الاتصال بالخادم");
        }
    });

    // =============================
    // 🕒 تحميل بيانات اليوم الحالي عند البداية
    // =============================
    const today = dateInput.value || new Date().toISOString().split("T")[0];
    loadAttendanceByDate(today);

    // ترقيم الصفوف
    filterTable();
});
