// gallery.js
class ProjectGallery {
    constructor() {
        this.currentPage = 1;
        this.loading = false;
        this.hasMore = true;
        this.projects = [];
        this.selectedProject = null;
        this.currentImageIndex = 0;
        
        // DOM элементы
        this.projectsTrack = document.getElementById('projectsTrack');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.modal = document.getElementById('projectModal');
        this.fullscreenModal = document.getElementById('fullscreenModal');
        this.modalLayout = document.getElementById('modalLayout');
        this.fullscreenImage = document.getElementById('fullscreenImage');
        
        // URL для API (замените на ваш)
        this.apiUrl = 'http://localhost:8000/constructs';
        
        this.init();
    }
    
    async init() {
        // Загружаем первые проекты
        await this.loadProjects();
        
        // Настраиваем бесконечный скролл
        this.setupInfiniteScroll();
        
        // Настраиваем обработчики событий
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Закрытие модального окна
        document.getElementById('closeModal').addEventListener('click', () => this.closeModal());
        
        // Закрытие по клику на фон
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });
        
        // Закрытие полноэкранного режима
        document.getElementById('closeFullscreen').addEventListener('click', () => this.closeFullscreen());
        this.fullscreenModal.addEventListener('click', (e) => {
            if (e.target === this.fullscreenModal) this.closeFullscreen();
        });
        
        // Закрытие по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.closeFullscreen();
            }
        });
    }
    
    setupInfiniteScroll() {
        const scrollContainer = document.querySelector('.projects-scroll');
        
        scrollContainer.addEventListener('scroll', () => {
            const { scrollLeft, scrollWidth, clientWidth } = scrollContainer;
            
            // Если доскроллили до конца
            if (scrollWidth - scrollLeft - clientWidth < 100) {
                if (!this.loading && this.hasMore) {
                    this.loadProjects();
                }
            }
        });
    }
    
    async loadProjects() {
        if (this.loading || !this.hasMore) return;
        
        this.loading = true;
        this.loadingSpinner.style.display = 'flex';
        
        try {
            const response = await fetch(`${this.apiUrl}/api/?page=${this.currentPage}`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.projects = [...this.projects, ...data.results];
                this.renderProjects(data.results);
                this.currentPage++;
                this.hasMore = !!data.next;
            } else {
                this.hasMore = false;
            }
        } catch (error) {
            console.error('Ошибка загрузки проектов:', error);
        } finally {
            this.loading = false;
            this.loadingSpinner.style.display = 'none';
        }
    }
    
    renderProjects(projects) {
        projects.forEach(project => {
            const card = this.createProjectCard(project);
            this.projectsTrack.appendChild(card);
        });
    }
    
    createProjectCard(project) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.id = project.id;
        
        // Фоновое изображение
        const imageUrl = project.main_image?.url || 'https://via.placeholder.com/300x400';
        
        card.innerHTML = `
            <div class="project-card-image" style="background-image: url('${imageUrl}')">
                <div class="project-card-overlay">
                    <h3 class="project-card-title">${project.title}</h3>
                    ${project.area ? `<div class="project-card-area">${project.area} м²</div>` : ''}
                    ${project.price ? `<div class="project-card-price">${this.formatPrice(project.price)} ₽</div>` : ''}
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => this.openProjectDetails(project.id));
        
        return card;
    }
    
    async openProjectDetails(projectId) {
        try {
            const response = await fetch(`${this.apiUrl}/products/${projectId}/`);
            const project = await response.json();
            
            this.selectedProject = project;
            this.currentImageIndex = 0;
            
            this.renderProjectModal(project);
            this.modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            
        } catch (error) {
            console.error('Ошибка загрузки деталей проекта:', error);
        }
    }
    
    renderProjectModal(project) {
        const mainImage = project.images[0]?.url || '';
        
        let characteristicsHtml = '';
        if (project.characteristics) {
            characteristicsHtml = project.characteristics.map(char => `
                <div class="characteristic-item">
                    <span class="characteristic-icon">${char.icon}</span>
                    <div class="characteristic-info">
                        <span class="characteristic-label">${char.label}</span>
                        <span class="characteristic-value">${char.value}</span>
                    </div>
                </div>
            `).join('');
        }
        
        let thumbnailsHtml = '';
        if (project.images && project.images.length > 0) {
            thumbnailsHtml = project.images.map((img, index) => `
                <div class="thumbnail ${index === 0 ? 'active' : ''}" data-index="${index}">
                    <img src="${img.url}" alt="${img.alt}">
                </div>
            `).join('');
        }
        
        this.modalLayout.innerHTML = `
            <div class="modal-gallery">
                <div class="main-image-container">
                    <img src="${mainImage}" alt="${project.title}" class="main-image" id="mainModalImage">
                </div>
                <div class="thumbnails-strip" id="thumbnailsStrip">
                    ${thumbnailsHtml}
                </div>
            </div>
            <div class="modal-info">
                <h2 class="project-detail-title">${project.title}</h2>
                ${project.article ? `<div class="project-article">Артикул: ${project.article}</div>` : ''}
                
                <div class="characteristics-grid">
                    ${characteristicsHtml}
                </div>
                
                <div class="price-section">
                    ${project.old_price ? `<div class="old-price">${this.formatPrice(project.old_price)} ₽</div>` : ''}
                    <div class="current-price">${this.formatPrice(project.price)} ₽</div>
                </div>
                
                ${project.description ? `
                    <div class="project-description">
                        <h3>Описание</h3>
                        <p>${project.description}</p>
                    </div>
                ` : ''}
                
                <div class="project-actions">
                    <button class="btn btn-primary">Заказать проект</button>
                    <button class="btn btn-secondary">В избранное</button>
                </div>
            </div>
        `;
        
        // Добавляем обработчики для галереи
        this.setupGalleryHandlers(project);
    }
    
    setupGalleryHandlers(project) {
        const mainImage = document.getElementById('mainModalImage');
        const thumbnails = document.querySelectorAll('.thumbnail');
        const thumbnailsStrip = document.getElementById('thumbnailsStrip');
        
        // Клик по миниатюре
        thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('click', () => {
                thumbnails.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
                mainImage.src = project.images[index].url;
                this.currentImageIndex = index;
            });
        });
        
        // Клик по главному изображению для полноэкранного режима
        mainImage.addEventListener('click', () => {
            this.openFullscreen(mainImage.src);
        });
        
        // Горизонтальный скролл миниатюр колесиком
        thumbnailsStrip.addEventListener('wheel', (e) => {
            e.preventDefault();
            thumbnailsStrip.scrollLeft += e.deltaY;
        });
    }
    
    openFullscreen(imageUrl) {
        this.fullscreenImage.src = imageUrl;
        this.fullscreenModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    closeFullscreen() {
        this.fullscreenModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    closeModal() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    formatPrice(price) {
        return new Intl.NumberFormat('ru-RU').format(price);
    }
}

// Инициализация галереи при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new ProjectGallery();
});