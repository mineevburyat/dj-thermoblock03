document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('constructionForm');
    const steps = document.querySelectorAll('.step');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const progressBar = document.querySelector('.progress-bar');
    const fileUploadSection = document.getElementById('fileUploadSection');
    const projectRadios = document.querySelectorAll('input[name="project_status"]');
    
    let currentStep = 1;
    const totalSteps = 3;
    
    // Иконки для типов строений
    const buildingIcons = {
        'house': 'home',
        'extension': 'plus-square',
        'garage': 'car',
        'banya': 'fire',
        'office': 'building',
        'warehouse': 'warehouse',
        'greenhouse': 'seedling',
        'other': 'question-circle'
    };
    
    // Обновляем иконки
    document.querySelectorAll('.building-type-card i').forEach(icon => {
        const type = icon.classList[1].split('-')[2];
        if (buildingIcons[type]) {
            icon.className = `fas fa-${buildingIcons[type]} fa-3x mb-3 text-primary`;
        }
    });
    
    // Показываем/скрываем загрузку файла
    projectRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'has_project' || this.value === 'has_sketch') {
                fileUploadSection.style.display = 'block';
            } else {
                fileUploadSection.style.display = 'none';
            }
        });
    });
    
    // Валидация шага
    function validateStep(step) {
        switch(step) {
            case 1:
                return document.querySelector('input[name="building_type"]:checked') !== null;
            case 2:
                return document.getElementById('floor_count').value !== '';
            case 3:
                const name = document.getElementById('name').value;
                const phone = document.getElementById('phone').value;
                const email = document.getElementById('email').value;
                const agree = document.getElementById('agree_terms').checked;
                const projectSelected = document.querySelector('input[name="project_status"]:checked') !== null;
                
                return name && phone && email && agree && projectSelected;
            default:
                return false;
        }
    }
    
    // Обновление прогресс-бара
    function updateProgressBar() {
        const percent = (currentStep / totalSteps) * 100;
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `Шаг ${currentStep} из ${totalSteps}`;
        progressBar.setAttribute('aria-valuenow', percent);
    }
    
    // Переход между шагами
    function showStep(step) {
        // Скрываем все шаги
        steps.forEach(s => {
            s.classList.remove('active');
            s.classList.add('d-none');
        });
        
        // Показываем текущий шаг
        const currentStepElement = document.querySelector(`.step-${step}`);
        currentStepElement.classList.remove('d-none');
        currentStepElement.classList.add('active');
        
        // Обновляем кнопки
        prevBtn.style.display = step === 1 ? 'none' : 'inline-block';
        nextBtn.style.display = step === totalSteps ? 'none' : 'inline-block';
        submitBtn.style.display = step === totalSteps ? 'inline-block' : 'none';
        
        // Обновляем прогресс бар
        updateProgressBar();
        
        // Прокручиваем к верху формы
        currentStepElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Обработчики кнопок
    nextBtn.addEventListener('click', function() {
        if (validateStep(currentStep)) {
            currentStep++;
            showStep(currentStep);
        } else {
            alert('Пожалуйста, заполните все обязательные поля перед продолжением.');
        }
    });
    
    prevBtn.addEventListener('click', function() {
        currentStep--;
        showStep(currentStep);
    });
    
    // Маска для телефона
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', function(e) {
        let x = e.target.value.replace(/\D/g, '').match(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
        e.target.value = !x[2] ? x[1] : '+7 (' + x[2] + ') ' + x[3] + (x[4] ? '-' + x[4] : '') + (x[5] ? '-' + x[5] : '');
    });
    
    // Валидация формы перед отправкой
    form.addEventListener('submit', function(e) {
        if (!validateStep(3)) {
            e.preventDefault();
            alert('Пожалуйста, заполните все обязательные поля.');
            return false;
        }
        
        // Показываем сообщение об успехе
        const modal = bootstrap.Modal.getInstance(document.getElementById('constructionModal'));
        modal.hide();
        
        setTimeout(() => {
            alert('Спасибо! Ваша заявка отправлена. Наш специалист свяжется с вами в ближайшее время.');
            form.reset();
            currentStep = 1;
            showStep(currentStep);
        }, 500);
    });
    
    // Инициализация
    showStep(currentStep);
});