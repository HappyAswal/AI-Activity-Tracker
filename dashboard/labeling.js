// Helper to get selected date or default to today
function getDateParam() {
    const datePicker = document.getElementById('datePicker');
    if (!datePicker.value) {
        const local = new Date();
        local.setMinutes(local.getMinutes() - local.getTimezoneOffset());
        datePicker.value = local.toJSON().slice(0, 10);
    }
    return datePicker.value;
}

// Load grouped labeling data
async function loadLabelingData() {
    const list = document.getElementById('labeling-list');
    list.innerHTML = '<div class="loading">Fetching data...</div>';

    try {
        const date = getDateParam();
        const response = await fetch(`/api/unique-activities?date=${date}`);
        const data = await response.json();

        if (data.length === 0) {
            list.innerHTML = '<div class="loading">No activities recorded yet</div>';
            return;
        }

        const categories = ['Productivity', 'Entertainment', 'Social Media', 'Communication', 'Other'];

        list.innerHTML = data.map((activity, index) => {
            const categoryClass = activity.category.toLowerCase().replace(' ', '-');

            const optionsHtml = categories.map(cat =>
                `<option value="${cat}" ${cat === activity.category ? 'selected' : ''}>${cat}</option>`
            ).join('');

            // To update, we just send a PUT to any string match endpoint. We need to create a dedicated batch endpoint to handle App+Title 
            return `
                <div class="activity-item">
                    <div class="activity-category category-${categoryClass}">
                        <select class="category-select" data-app="${escapeHtml(activity.app_name)}" data-title="${escapeHtml(activity.window_title)}" onchange="batchUpdateCategory(this)">
                            ${optionsHtml}
                        </select>
                    </div>
                    <div class="activity-details">
                        <div class="activity-app">${escapeHtml(activity.app_name)}</div>
                        <div class="activity-title">${escapeHtml(activity.window_title)}</div>
                    </div>
                    <div class="badge">
                        📁 ${activity.instances} instances
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error(e);
        list.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// Basic HTML escaper
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Perform a batch update based on app and title
async function batchUpdateCategory(selectElement) {
    const newCategory = selectElement.value;
    const appName = selectElement.getAttribute('data-app');
    const windowTitle = selectElement.getAttribute('data-title');

    // We must unescape the HTML entities to send the raw string back to the DB
    const unescapeHtml = (safe) => {
        if (!safe) return '';
        const doc = new DOMParser().parseFromString(safe, "text/html");
        return doc.documentElement.textContent;
    };

    selectElement.parentElement.className = `activity-category category-${newCategory.toLowerCase().replace(' ', '-')}`;

    try {
        const response = await fetch('/api/activity/batch', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                app_name: unescapeHtml(appName),
                window_title: unescapeHtml(windowTitle),
                category: newCategory
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Batch update failed:', error);
        alert('Failed to update database bulk rows.');
        loadLabelingData();
    }
}

// Trigger AI retraining and notify active tracker
async function retrainAI() {
    try {
        const btn = document.querySelector('div[onclick="retrainAI()"]');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="refresh-icon">⏳</span> Training...';
        btn.style.pointerEvents = 'none';

        const response = await fetch('/api/retrain', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alert('AI Brain successfully retrained!\n\nThe live tracker will instantly sync to this new memory on its next check.');
        } else {
            alert('Failed to retrain AI: ' + (result.error || 'Unknown error'));
        }

        btn.innerHTML = originalHtml;
        btn.style.pointerEvents = 'auto';
    } catch (error) {
        console.error('Retrain failed:', error);
        alert('Could not trigger AI retraining.');
    }
}

// Auto-refresh every 60 seconds
setInterval(loadLabelingData, 60000);
loadLabelingData();
