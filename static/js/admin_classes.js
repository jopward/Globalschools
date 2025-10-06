<script>
document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('#classes-table tbody');
    const searchInput = document.querySelector('#search-input');

    // 🔹 تحميل جميع الصفوف للمدرسة الحالية
    function loadClasses() {
        fetch('/classes/filter/school')
            .then(response => {
                if (!response.ok) throw new Error('خطأ في تحميل الصفوف');
                return response.json();
            })
            .then(data => {
                tableBody.innerHTML = '';
                if (data.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="4" class="text-center">لا توجد صفوف حالياً</td></tr>';
                    return;
                }
                data.forEach(cls => {
                    const row = `
                        <tr>
                            <td>${cls.id}</td>
                            <td>${cls.class_name || '-'}</td>
                            <td>${cls.section || '-'}</td>
                            <td>${cls.period || '-'}</td>
                        </tr>
                    `;
                    tableBody.insertAdjacentHTML('beforeend', row);
                });
            })
            .catch(err => {
                console.error(err);
                tableBody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">حدث خطأ أثناء تحميل الصفوف</td></tr>';
            });
    }

    // 🔹 البحث عن الصفوف حسب الاسم
    searchInput.addEventListener('input', () => {
        const keyword = searchInput.value.trim();
        if (keyword === '') {
            loadClasses();
            return;
        }
        fetch(`/classes/search?keyword=${encodeURIComponent(keyword)}`)
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
                if (data.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="4" class="text-center">لا توجد نتائج</td></tr>';
                    return;
                }
                data.forEach(cls => {
                    const row = `
                        <tr>
                            <td>${cls.id}</td>
                            <td>${cls.class_name || '-'}</td>
                            <td>${cls.section || '-'}</td>
                            <td>${cls.period || '-'}</td>
                        </tr>
                    `;
                    tableBody.insertAdjacentHTML('beforeend', row);
                });
            });
    });

    // 🔹 تحميل الصفوف عند فتح الصفحة
    loadClasses();
});
</script>
