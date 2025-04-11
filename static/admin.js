// Admin Interface Functionality
document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.admin-section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            navButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            button.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });

    // Template Editor
    const editor = ace.edit('json-editor');
    editor.setTheme('ace/theme/monokai');
    editor.session.setMode('ace/mode/json');
    editor.setOptions({
        fontSize: '14px',
        tabSize: 2,
        useSoftTabs: true,
        wrap: true
    });

    // Template Management
    const addTemplateBtn = document.querySelector('.add-template-btn');
    const templateModal = document.getElementById('template-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const saveTemplateBtn = document.querySelector('.save-btn');
    const publishTemplateBtn = document.querySelector('.publish-btn');

    addTemplateBtn.addEventListener('click', () => {
        templateModal.style.display = 'block';
        editor.setValue(JSON.stringify({
            name: '',
            fields: [],
            validation: {},
            layout: {}
        }, null, 2));
    });

    closeModalBtn.addEventListener('click', () => {
        templateModal.style.display = 'none';
    });

    saveTemplateBtn.addEventListener('click', () => {
        try {
            const template = JSON.parse(editor.getValue());
            // Save template logic here
            console.log('Template saved:', template);
        } catch (error) {
            alert('Invalid JSON format');
        }
    });

    publishTemplateBtn.addEventListener('click', () => {
        try {
            const template = JSON.parse(editor.getValue());
            // Publish template logic here
            console.log('Template published:', template);
        } catch (error) {
            alert('Invalid JSON format');
        }
    });

    // AI Suggestions
    const trainModelBtn = document.querySelector('.train-model-btn');
    const exportDataBtn = document.querySelector('.export-data-btn');
    const autoCompletionThreshold = document.getElementById('auto-completion-threshold');
    const learningRate = document.getElementById('learning-rate');

    trainModelBtn.addEventListener('click', () => {
        // Train model logic here
        console.log('Training model with settings:', {
            threshold: autoCompletionThreshold.value,
            learningRate: learningRate.value
        });
    });

    exportDataBtn.addEventListener('click', () => {
        // Export training data logic here
        console.log('Exporting training data');
    });

    // Statistics
    const dateRange = document.getElementById('date-range');
    const applyRangeBtn = document.querySelector('.apply-range-btn');

    applyRangeBtn.addEventListener('click', () => {
        // Update statistics based on date range
        console.log('Applying date range:', dateRange.value);
        updateStatistics();
    });

    // Initialize charts
    const usageChart = new Chart(document.getElementById('usage-chart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Template Usage',
                data: [],
                borderColor: '#4CAF50',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    const accuracyChart = new Chart(document.getElementById('accuracy-chart'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'OCR Accuracy',
                data: [],
                backgroundColor: '#2196F3'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    function updateStatistics() {
        // Fetch and update statistics data
        // This is a placeholder - implement actual data fetching
        const mockData = {
            usage: [10, 20, 30, 40, 50],
            accuracy: [85, 90, 88, 92, 95],
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        };

        usageChart.data.labels = mockData.labels;
        usageChart.data.datasets[0].data = mockData.usage;
        usageChart.update();

        accuracyChart.data.labels = mockData.labels;
        accuracyChart.data.datasets[0].data = mockData.accuracy;
        accuracyChart.update();
    }

    // Initialize with default data
    updateStatistics();
}); 