const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const closeModalBtn = document.getElementById('close-modal');
const saveSettingsBtn = document.getElementById('save-settings');
const saveIndicator = document.getElementById('save-indicator');

const themeSelect = document.getElementById('theme-select');
const botNameInput = document.getElementById('bot-name');
const userNameInput = document.getElementById('user-name');
const districtInput = document.getElementById('district');
const areaInput = document.getElementById('user-area');
const cityInput = document.getElementById('city');
const streetInput = document.getElementById('street');
const phoneInput = document.getElementById('user-phone');
const emailInput = document.getElementById('user-email');

const svgImage = `<svg xmlns="http://www.w3.org/2000/svg" fill="#FFF" stroke-miterlimit="10" stroke-width="2" viewBox="0 0 96 96">
  <path stroke="#979593" d="M67.1716 7H27c-1.1046 0-2 .8954-2 2v78c0 1.1046.8954 2 2 2h58c1.1046 0 2-.8954 2-2V26.8284c0-.5304-.2107-1.0391-.5858-1.4142L68.5858 7.5858C68.2107 7.2107 67.702 7 67.1716 7z"/>
  <path fill="none" stroke="#979593" d="M67 7v18c0 1.1046.8954 2 2 2h18"/>
  <path fill="#C8C6C4" d="M79 61H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0 24H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1z"/>
  <path fill="#185ABD" d="M12 74h32c2.2091 0 4-1.7909 4-4V38c0-2.2091-1.7909-4-4-4H12c-2.2091 0-4 1.7909-4 4v32c0 2.2091 1.7909 4 4 4z"/>
  <path d="M21.6245 60.6455c.0661.522.109.9769.1296 1.3657h.0762c.0306-.3685.0889-.8129.1751-1.3349.0862-.5211.1703-.961.2517-1.319L25.7911 44h4.5702l3.6562 15.1272c.183.7468.3353 1.6973.457 2.8532h.0608c.0508-.7979.1777-1.7184.3809-2.7615L37.8413 44H42l-5.1183 22h-4.86l-3.4885-14.5744c-.1016-.4197-.2158-.9663-.3428-1.6417-.127-.6745-.2057-1.1656-.236-1.4724h-.0608c-.0407.358-.1195.8896-.2364 1.595-.1169.7062-.211 1.2273-.2819 1.565L24.1 66h-4.9357L14 44h4.2349l3.1843 15.3882c.0709.3165.1392.7362.2053 1.2573z"/>
</svg>`

const SettingsManager = (function() {
    // Начальные настройки
    const defaultSettings = {
        theme: 'dark',
        botName: 'Долгострой',
        username: "",
        district: "",
        area: "",
        city: "",
        street: "",
        phone: "",
        email: ""
    };

    function getSettings() {
        const savedSettings = localStorage.getItem('chatbot-settings');
        return savedSettings ? JSON.parse(savedSettings) : defaultSettings;
    }

    function saveSettings(settings) {
        localStorage.setItem('chatbot-settings', JSON.stringify(settings));
    }

    function applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
    }

    function loadSettingsIntoForm() {
        const settings = getSettings();
        themeSelect.value = settings.theme;
        botNameInput.value = settings.botName;
        userNameInput.value = settings.username;
        districtInput.value = settings.district;
        areaInput.value = settings.area;
        cityInput.value = settings.city;
        streetInput.value = settings.street;
        emailInput.value = settings.email;
        phoneInput.value = settings.phone;
    }

    function applyAllSettings() {
        const settings = getSettings();
        applyTheme(settings.theme);
        document.querySelector('.logo h1').textContent = settings.botName;
        document.title = settings.botName;
    }

    function updateSettings() {
        const settings = {
            theme: themeSelect.value,
            botName: botNameInput.value || defaultSettings.botName,
            username: userNameInput.value,
            district: districtInput.value,
            area: areaInput.value,
            city: cityInput.value,
            street: streetInput.value,
            phone: phoneInput.value,
            email: emailInput.value
        };
        
        saveSettings(settings);
        applyAllSettings();
        
        // Show save confirmation
        saveIndicator.style.display = 'block';
        setTimeout(() => {
            saveIndicator.style.display = 'none';
        }, 2000);

        return settings;
    }

    function init() {
        applyAllSettings();
    }

    return {
        getSettings,
        loadSettingsIntoForm,
        updateSettings,
        init
    };
})();

// Менеджер скриптов необходим для отслеживания событий начала скрпита,
// процесса выполнения и его завершения.
// Каждый скрипт имеет состояние создаваемое в init функции, 
// В состоянии должно быть поле step - шаг выпонения скрипта первый, второй и т.д.
//
// Шаг может быть использован в ЧатБоте для начала/завершения других сценариев.
// Каждый сценарий работы должен иметь init, process, end и isActive функции
// За переключение между сценариями отвечает функция getResponse бот
// 
// Для вызова функции end скрипта достаточно присвоить переменной activeScript -> null 
// в теле функции process

const ScriptManager = (function() {
    // Хранит прошлое название скрипта необходимое для endScript функции
    let tempNameScript = null;
    let activeScript = null; // имя активного скрипта
    let scriptState = {}; // состояние скрипта
    let scriptData = {}; // дополнительная информация
    

    const scriptScenarios = {
        
        // После себя сразу вызывает userInput сценарий
        findTemplate: {
            init: function(data) {
                scriptState = {
                    userData: data || {},
                    step: 1
                };
                findTemplateFlag = true;
                return "Какой шаблон постановления вы бы хотели заполнить?";
    
            },
            
            process: async function(userResponse) {
                scriptState.step++;
                try {
                    const response = await fetch("/api/search/template", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ message: userResponse })
                    });
                    const data = await response.json();
                    scriptState.userData = data.info;
                    console.log(data);
                    // Завершение работы скрипта
                    activeScript = null;
                    return data.response;
            
                } catch (error) {
                    activeScript = null;
                    return `Ошибка: ${error}`;
                }
        
            },
            end: function(){
                findTemplateFlag = false;
                UIManager.addMessage(startScript("userInput", scriptState.userData));
            },
            
            isActive: function() {
                return activeScript === 'findTemplate';
            }
            
        },
        userInput: {
            init: function(data) {
                if (!data || typeof data !== 'object') {
                    console.error('Invalid data received:', data);
                    return "Ошибка: Неверные данные шаблона";
                }

                // Create a safe copy of the data
                scriptData = JSON.parse(JSON.stringify(data));
                
                // Initialize state with default values
                scriptState = {
                    currentSection: 'user_input',
                    currentFieldIndex: 0,
                    collectedData: {},
                    step: 1,
                    fields: [],
                    url: ""
                };

                // Safely get fields from data
                if (scriptData.user_input && typeof scriptData.user_input === 'object') {
                    scriptState.fields = Object.keys(scriptData.user_input);
                } else {
                    console.error('No user_input found in template data:', scriptData);
                    return "Ошибка: Шаблон не содержит полей для ввода";
                }

                if (scriptState.fields.length === 0) {
                    return "Ошибка: Шаблон не содержит полей для ввода";
                }

                const firstField = scriptState.fields[0];
                const prompt = scriptData.user_input[firstField] || `Введите ${firstField}`;
                return `Введите необходимые данные для заполнения формы: \n ${prompt}:`;
            },
            
            process: async function(userResponse) {
                scriptState.step++;

                const currentField = scriptState.fields[scriptState.currentFieldIndex];
                
                scriptState.collectedData[currentField] = userResponse.trim();
                
                scriptState.currentFieldIndex++;
                
                if (scriptState.currentFieldIndex >= scriptState.fields.length) {
                    for (const field in scriptState.collectedData) {
                        if (scriptData.user_input) {
                            scriptData.user_input[field] = scriptState.collectedData[field];
                        }
                    }
                    
                    // Reset active script
                    const completedData = scriptData;
                    fillFieldOfSettings(completedData);
                    console.log(completedData);

                    try {
                        const response = await fetch("/api/document/create", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(completedData)
                        });
                        const data = await response.json();
                        scriptState.url = data.url;
                    } catch (error) {
                        return `Ошибка ${error}`;
                    }
                    activeScript = null;
                    return "Спасибо! Все данные успешно собраны."
                } else {
                    // Get next field to prompt for
                    const nextField = scriptState.fields[scriptState.currentFieldIndex];
                    const prompt = scriptData.user_input[nextField] || `Введите ${nextField}`;
                    return `${prompt}:`;
                }
            },
            
            isActive: function() {
                return activeScript === 'userInput';
            },

            end: function(){
                if (scriptState.url) {
                    UIManager.addDocumentMessage(scriptState.url, "document.docx");
                } else {
                    console.error('No document URL available');
                    UIManager.addMessage("Ошибка: Не удалось создать документ");
                }
            }
        },
    };
    
    function startScript(scenarioName, initialData) {
        if (scriptScenarios.hasOwnProperty(scenarioName)) {
            console.log(`Начало работы: ${scenarioName}`);
            tempNameScript = scenarioName;
            activeScript = scenarioName;
            
            return scriptScenarios[scenarioName].init(initialData);
        } else {
            console.log(`Такого скрипта нет: ${scenarioName}`);
        }
        return null;
    }
    
    // Процесс выполнения какого либо сценария
    function processScriptInput(userInput) {
        console.log(`Шаг выполнения: ${scriptState.step}`);
        if (activeScript && scriptScenarios[activeScript]) {
            tempNameScript = activeScript;
            return scriptScenarios[activeScript].process(userInput);
        }
        return null;
    }
    
    function isScriptActive() {
        return activeScript !== null;
    }
    

    function isScenarioActive(scenarioName) {
        return activeScript === scenarioName;
    }
    
    function endScript() {
        console.log(`Конец работы: ${tempNameScript}`);
        if (tempNameScript) scriptScenarios[tempNameScript].end();
    }

    function checkEndOfExecutionScript(){
        return tempNameScript !== null;
    }
    
    function getScriptData() {
        return {
            scenario: activeScript,
            temp: tempNameScript,
            state: scriptState,
            data: scriptData
        };
    }

    return {
        startScript,
        processScriptInput,
        isScriptActive,
        isScenarioActive,
        endScript,
        getScriptData,
        checkEndOfExecutionScript
    };
})();

const ChatBot = (function() {
    function getResponse(message) {
        if (ScriptManager.isScriptActive()) {
            const scriptResponse = ScriptManager.processScriptInput(message);
            // Можно впихнуть сюда пост обработку ответа сервера
            return scriptResponse;
        }
        return "Ошибка";
    }
    
    return {
        getResponse
    };
})();


const UIManager = (function() {
    function addMessage(text, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const messageText = document.createElement('div');
        messageText.textContent = text;
        messageElement.appendChild(messageText);
        
        const timestamp = document.createElement('div');
        timestamp.classList.add('message-timestamp');
        const now = new Date();
        timestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        messageElement.appendChild(timestamp);
        
        chatMessages.appendChild(messageElement);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    function addDocumentMessage(documentUrl, documentName, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const documentContainer = document.createElement('div');
        documentContainer.classList.add('document-container');
        
        const documentLink = document.createElement('a');
        documentLink.href = documentUrl;
        documentLink.download = documentName || 'document';
        documentLink.classList.add('document-link');
        
        const documentImage = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        documentImage.innerHTML = svgImage;
        documentImage.classList.add("document-image");
        
        // подпись к документу
        const documentLabel = document.createElement('div');
        documentLabel.textContent = documentName || 'Document';
        documentLabel.classList.add('document-label');
        
        documentLink.appendChild(documentImage);
        documentLink.appendChild(documentLabel);
        documentContainer.appendChild(documentLink);
        messageElement.appendChild(documentContainer);
        
        // добавление временной метки
        const timestamp = document.createElement('div');
        timestamp.classList.add('message-timestamp');
        const now = new Date();
        timestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        messageElement.appendChild(timestamp);
        
        chatMessages.appendChild(messageElement);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    // Типо текст набирает
    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('typing-indicator');
        typingElement.id = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            typingElement.appendChild(dot);
        }
        
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function setupTextareaResize() {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            const newHeight = Math.min(this.scrollHeight, 120);
            this.style.height = newHeight + 'px';
        });
    }

    // Return public methods
    return {
        addMessage,
        showTypingIndicator,
        hideTypingIndicator,
        setupTextareaResize,
        addDocumentMessage
    };
})();

function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        UIManager.addMessage(message, true);
        
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        UIManager.showTypingIndicator();
        
        setTimeout(async () => {
            const botResponse = await ChatBot.getResponse(message);
            UIManager.hideTypingIndicator();
            UIManager.addMessage(botResponse);
            if (ScriptManager.checkEndOfExecutionScript() && !ScriptManager.isScriptActive()) {
                ScriptManager.endScript();
            }
        }, 200);
    }
}

function fillFieldOfSettings(data){
    settings = SettingsManager.getSettings();
    data.settings.fullname = settings.username;
    data.settings.email = settings.email;
    data.settings.phone = settings.phone;
    data.settings.street = settings.street;
    data.settings.city = settings.city;
    data.settings.area = settings.area;
    data.settings.district = settings.district;
}

sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

settingsBtn.addEventListener('click', function() {
    SettingsManager.loadSettingsIntoForm();
    settingsModal.style.display = 'block';
});

closeModalBtn.addEventListener('click', function() {
    settingsModal.style.display = 'none';
});

window.addEventListener('click', function(e) {
    if (e.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
});

saveSettingsBtn.addEventListener('click', function() {
    SettingsManager.updateSettings();
    setTimeout(() => {
        settingsModal.style.display = 'none';
    }, 1500);
});

function init() {
    SettingsManager.init();
    UIManager.setupTextareaResize();
    UIManager.addMessage(ScriptManager.startScript("findTemplate"));
}

// File Drag & Drop Handling
const dragOverlay = document.getElementById('drag-overlay');
let dragCounter = 0;

// These events need to be on the document to catch dragging anywhere on the page
document.addEventListener('dragenter', (e) => {
    e.preventDefault();
    dragCounter++;
    
    // Only show overlay if file is being dragged
    if (e.dataTransfer.types.includes('Files')) {
        dragOverlay.classList.add('active');
    }
});

document.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dragCounter--;
    
    // Only hide if we've left all drag areas
    if (dragCounter <= 0) {
        dragCounter = 0;
        dragOverlay.classList.remove('active');
    }
});

document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    dragCounter = 0;
    dragOverlay.classList.remove('active');
    
    const uploadArea = document.getElementById('upload-area');
    
    // Only process if files were dropped
    if (e.dataTransfer.files.length > 0) {
        const droppedFile = e.dataTransfer.files[0]; // Store the file in a variable
        // If dropped on upload area, handle directly
        if (uploadArea && uploadArea.contains(e.target)) {
            console.log("Файл кинули");
            handleFileUpload(droppedFile);
        } else {
            // If dropped elsewhere, show document section and handle
            
                setTimeout(() => {
                    console.log("Файл кинули после проверок");
                    handleFileUpload(droppedFile); // Use the stored file
                }, 300);
            
        }
    }
});

// Document Processing Variables
let closeDocumentBtn, progressBar, progressText, confidenceBar, confidenceText;
let chipCategories, chipsContainer, generateBtn, previewBtn, previewModal;
let closePreviewBtn, downloadBtn, uploadDocBtn, fileInput, uploadArea;
let templateSuggestions, formFields;
let findTemplateFlag = true;

// Initialize DOM elements
function initializeElements() {
    closeDocumentBtn = document.getElementById('close-document-btn');
    progressBar = document.getElementById('progress-fill');
    progressText = document.getElementById('progress-text');
    confidenceBar = document.getElementById('confidence-fill');
    confidenceText = document.getElementById('confidence-text');
    chipCategories = document.querySelectorAll('.chip-category');
    chipsContainer = document.getElementById('chips-container');
    generateBtn = document.getElementById('generate-btn');
    previewBtn = document.getElementById('preview-btn');
    previewModal = document.getElementById('preview-modal');
    closePreviewBtn = document.getElementById('close-preview-btn');
    downloadBtn = document.getElementById('download-btn');
    uploadDocBtn = document.getElementById('upload-doc-btn');
    fileInput = document.getElementById('document-upload');
    uploadArea = document.getElementById('upload-area');
    templateSuggestions = document.getElementById('template-suggestions');
    formFields = document.getElementById('form-fields');
    
    // Initialize event listeners if elements exist
    if (fileInput && uploadArea) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const selectedFile = e.target.files[0];
                console.log("Файл выбран через диалог", selectedFile);
                handleFileUpload(selectedFile);
            }
        });

        // Set up the upload button to trigger file input click
        if (uploadDocBtn) {
            uploadDocBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
            uploadArea.style.borderColor = 'var(--primary-color)';
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
            uploadArea.style.borderColor = 'var(--border-color)';
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            uploadArea.style.borderColor = 'var(--border-color)';
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }
    
    if (chatInput && templateSuggestions) {
        chatInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                templateSuggestions.style.display = 'none';
                return;
            }

            try {
                const response = await fetch('/api/templates/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query }),
                });

                if (!response.ok) {
                    throw new Error('Failed to search templates');
                }
// FIX 
                const data = await response.json();
                if (data.templates && Array.isArray(data.templates)) {
                    if(findTemplateFlag){
                        displayTemplateSuggestions(data.templates);
                    } else {
                        templateSuggestions.style.display = 'none';
                    }
                } else {
                    console.error('Invalid response format:', data);
                    templateSuggestions.style.display = 'none';
                }
            } catch (error) {
                console.error('Error searching templates:', error);
                templateSuggestions.style.display = 'none';
            }
        });
    }

    

    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const formData = collectFormData();
            try {
                const response = await fetch('/api/documents/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                const result = await response.json();
                showPreview(result.documentUrl);
            } catch (error) {
                console.error('Error generating document:', error);
                showError('Failed to generate document');
            }
        });
    }

    if (previewBtn) {
        previewBtn.addEventListener('click', () => {
            const formData = collectFormData();
            showPreview(formData);
        });
    }

    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', () => {
            previewModal.style.display = 'none';
        });
    }

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const previewFrame = document.getElementById('preview-frame');
            const link = document.createElement('a');
            link.href = previewFrame.src;
            link.download = 'document.pdf';
            link.click();
        });
    }

    // Initialize chip categories
    if (chipCategories && chipCategories.length > 0) {
        chipCategories.forEach(category => {
            category.addEventListener('click', () => {
                chipCategories.forEach(c => c.classList.remove('active'));
                category.classList.add('active');
                filterChips(category.dataset.category);
            });
        });
    }
}

// Call initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    init();
    
    
});

function displayTemplateSuggestions(templates) {
    templateSuggestions.innerHTML = '';
    
    if (!templates || templates.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'template-suggestion';
        noResults.textContent = 'Ничего не найдено';
        templateSuggestions.appendChild(noResults);
    } else {
        templates.forEach(template => {
            const div = document.createElement('div');
            div.className = 'template-suggestion';
            
            const name = document.createElement('div');
            name.className = 'template-name';
            name.textContent = template.name;
            
            const description = document.createElement('div');
            description.className = 'template-description';
            description.textContent = template.description || '';
            
            div.appendChild(name);
            div.appendChild(description);
            div.onclick = () => selectTemplate(template);
            templateSuggestions.appendChild(div);
        });
    }
    
    templateSuggestions.style.display = 'block';
}

async function selectTemplate(template) {
    chatInput.value = template.name;
    templateSuggestions.style.display = 'none';
    
    try {
        const response = await fetch(`/api/template/${template.id}`);
        if (!response.ok) {
            throw new Error('Failed to load template');
        }
        
        const templateData = await response.json();
        loadTemplateData(templateData);
    } catch (error) {
        console.error('Error loading template:', error);
        showError('Не удалось загрузить шаблон. Пожалуйста, попробуйте снова.');
    }
}

function validateFile(file) {
    // Check if file is undefined or null
    if (!file) {
        showError('Ошибка: Файл не найден или не выбран.');
        return false;
    }
    
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png'];
    const maxSize = 20 * 1024 * 1024; // 20MB

    if (!validTypes.includes(file.type)) {
        showError('Неподдерживаемый формат файла. Пожалуйста, загрузите PDF, DOCX, JPEG или PNG файл.');
        return false;
    }

    if (file.size > maxSize) {
        showError('Размер файла превышает лимит в 20MB.');
        return false;
    }

    return true;
}

async function loadTemplateData(templateData) {
    try {
        const formFields = document.getElementById('form-fields');
        const dataEntryForm = document.getElementById('data-entry-form');
        
        if (!formFields) {
            throw new Error('Form fields container not found');
        }

        // Clear previous form fields
        formFields.innerHTML = '';
        
        // Add fields from template data
        if (templateData.fields) {
            Object.entries(templateData.fields).forEach(([key, value]) => {
                const fieldDiv = document.createElement('div');
                fieldDiv.className = 'form-field';
                
                const label = document.createElement('label');
                label.textContent = key;
                
                const input = document.createElement('input');
                input.type = 'text';
                input.name = key;
                input.placeholder = value;
                
                fieldDiv.appendChild(label);
                fieldDiv.appendChild(input);
                formFields.appendChild(fieldDiv);
            });
        }
        
        // Show the form
        if (dataEntryForm) {
            dataEntryForm.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error loading template data:', error);
        showError('Ошибка при загрузке данных шаблона');
    }
}

async function handleFileUpload(file) {
    try {
        if (!validateFile(file)) return;


        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/document/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Ошибка загрузки файла' }));
            throw new Error(errorData.error || 'Ошибка загрузки файла');
        }

        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }

        if (result.structure && result.entities) {
            processDocument(result);
        } else {
            throw new Error('Неверный формат ответа от сервера');
        }
    } catch (error) {
        console.error('Ошибка при загрузке файла:', error);
        showError(error.message || 'Не удалось загрузить документ. Пожалуйста, попробуйте снова.');
    }
}

function showError(message) {
    console.log(`Ошибка при получении данных с сервера${message}`);
}

function processDocument(data) {
    if (!data) {
        showError('Не удалось обработать документ: отсутствуют данные');
        return;
    }

    // Show upload progress
    const uploadProgress = document.getElementById('upload-progress');
    if (!uploadProgress) {
        showError('Ошибка: элемент прогресса не найден');
        return;
    }

    const progressFill = uploadProgress.querySelector('.progress-fill');
    const progressText = uploadProgress.querySelector('.progress-text');
    
    if (!progressFill || !progressText) {
        showError('Ошибка: элементы прогресса не найдены');
        return;
    }
    
    uploadProgress.style.display = 'block';
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += 10;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Обработка документа... ${progress}%`;
        
        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                uploadProgress.style.display = 'none';
                showDataEntryForm(data);
            }, 500);
        }
    }, 200);
}

function showDataEntryForm(data) {
    if (!data || !data.entities || !Array.isArray(data.entities)) {
        console.error('Invalid data format:', data);
        showError('Ошибка: неверный формат данных');
        return;
    }

    try {
        // Create a formatted message with the extracted data
        let message = "Извлеченные данные из документа:\n\n";
        console.log(data.entities);
        // Group entities by type and format them
        const groupedEntities = {};
        data.entities.forEach(entity => {
            if (entity.label && entity.text) {
                if (!groupedEntities[entity.label]) {
                    groupedEntities[entity.label] = [];
                }
                // Add only unique entities
                if (!groupedEntities[entity.label].includes(entity.text)) {
                    groupedEntities[entity.label].push(entity.text);
                }
            }
        });

        // Add grouped entities to the message
        Object.entries(groupedEntities).forEach(([label, values]) => {
            message += `**${label}**:\n`;
            values.forEach(value => {
                message += `- ${value}\n`;
            });
            message += "\n";
        });

        // Add raw text preview if available
        if (data.structure && data.raw_text) {
            message += "**Полный текст**:\n";
            message += data.raw_text.substring(0, 200) + "...\n";
        }

        // Send the message through the bot
        UIManager.addMessage(message);

    } catch (error) {
        console.error('Error processing document data:', error);
        showError('Ошибка при обработке данных документа');
    }
}

// Chip System
function filterChips(category) {
    if (!chipsContainer) {
        console.error('Chips container not found');
        return;
    }
    
    const chips = chipsContainer.querySelectorAll('.chip');
    if (chips.length === 0) {
        console.warn('No chips found in container');
        return;
    }
    
    chips.forEach(chip => {
        chip.style.display = chip.dataset.category === category ? 'flex' : 'none';
    });
}

function toggleChip(chip) {
    if (!chip) {
        console.error('Invalid chip element');
        return;
    }
    chip.classList.toggle('selected');
}

function collectFormData() {
    const data = {};
    const fields = formFields.querySelectorAll('.form-field');
    fields.forEach(field => {
        const label = field.querySelector('label').textContent;
        const value = field.querySelector('input').value;
        data[label] = value;
    });
    return data;
}

// Preview Modal
function showPreview(documentUrl) {
    const previewFrame = document.getElementById('preview-frame');
    previewFrame.src = documentUrl;
    previewModal.style.display = 'flex';
}