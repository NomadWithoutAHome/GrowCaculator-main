// Plant grid and selection logic
export function initializePlantGrid() {
// Exported for UI image updates
function updatePlantImage(plantName) {
    const plantEmojiContainer = document.getElementById('plant-emoji');
    if (!plantEmojiContainer) return;
    const plantImage = document.getElementById('plant-image');
    const plantPlaceholder = document.getElementById('plant-placeholder');
    if (!plantImage || !plantPlaceholder) return;
    const filename = plantName.toLowerCase().replace(/\s+/g, '-').replace(/'/g, '');
    const imagePath = `/static/img/crop-${filename}.webp`;
    plantImage.src = imagePath;
    plantImage.alt = plantName;
    plantImage.onerror = function() {
        plantImage.style.display = 'none';
        plantPlaceholder.style.display = 'block';
    };
    plantImage.onload = function() {
        plantImage.style.display = 'block';
        plantPlaceholder.style.display = 'none';
    };
}

export { updatePlantImage };
    const plantGrid = document.getElementById('plant-grid');
    const searchInput = document.getElementById('plant-search');
    
    if (!plantGrid) {
        console.warn('Plant grid not found');
        return;
    }
    
    console.log('Initializing plant grid...');
    
    // Add click handlers to plant buttons
    plantGrid.addEventListener('click', function(e) {
        const plantButton = e.target.closest('[data-plant]');
        if (!plantButton) return;
        
        console.log('Plant clicked:', plantButton.dataset.plant);
        
        // Remove previous selection - look for any selected plant
        const previousSelected = plantGrid.querySelector('[aria-pressed="true"]');
        if (previousSelected) {
            previousSelected.classList.remove('bg-green-800', 'border-green-600', 'ring-2', 'ring-green-400');
            previousSelected.classList.add('bg-gray-700', 'border-gray-600');
            previousSelected.setAttribute('aria-pressed', 'false');
        }
        
        // Add selection to clicked plant
        plantButton.classList.remove('bg-gray-700', 'border-gray-600');
        plantButton.classList.add('bg-green-800', 'border-green-600', 'ring-2', 'ring-green-400');
        plantButton.setAttribute('aria-pressed', 'true');
        
        // Update current plant
        window.currentPlant = plantButton.dataset.plant;
        console.log('Selected plant:', window.currentPlant);
        
        // Update plant image
        if (window.updatePlantImage) {
            window.updatePlantImage(window.currentPlant);
        }
        
        // Update weight range first, then trigger calculation when complete
        if (window.updateWeightRange && window.updateCalculationIfReady) {
            window.updateWeightRange().then(() => {
                console.log('Weight range update complete, now triggering calculation...');
                window.updateCalculationIfReady();
            }).catch(error => {
                console.error('Error updating weight range:', error);
                window.updateCalculationIfReady();
            });
        }
    });
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            console.log('Searching for:', searchTerm);
            
            const plantButtons = plantGrid.querySelectorAll('[data-plant]');
            
            plantButtons.forEach(button => {
                const plantName = button.dataset.plant.toLowerCase();
                if (plantName.includes(searchTerm)) {
                    button.style.display = '';
                } else {
                    button.style.display = 'none';
                }
            });
        });
    } else {
        console.warn('Search input not found');
    }
    
    // Select default plant (Carrot)
    const defaultPlant = plantGrid.querySelector('[data-plant="Carrot"]');
    if (defaultPlant) {
        console.log('Setting default plant: Carrot');
        defaultPlant.classList.remove('bg-gray-700', 'border-gray-600');
        defaultPlant.classList.add('bg-green-800', 'border-green-600', 'ring-2', 'ring-green-400');
        defaultPlant.setAttribute('aria-pressed', 'true');
        window.currentPlant = 'Carrot';
        
        // Update plant image for default plant
        if (window.updatePlantImage) {
            window.updatePlantImage('Carrot');
        }
    } else {
        console.warn('Default plant (Carrot) not found');
    }
    
    // Preload all plant images
    if (window.preloadPlantImages) {
        window.preloadPlantImages();
    }
}

// Exported for UI image updates
function updatePlantImage(plantName) {
    const plantEmojiContainer = document.getElementById('plant-emoji');
    if (!plantEmojiContainer) return;
    const plantImage = document.getElementById('plant-image');
    const plantPlaceholder = document.getElementById('plant-placeholder');
    if (!plantImage || !plantPlaceholder) return;
    const filename = plantName.toLowerCase().replace(/\s+/g, '-').replace(/'/g, '');
    const imagePath = `/static/img/crop-${filename}.webp`;
    plantImage.src = imagePath;
    plantImage.alt = plantName;
    plantImage.onerror = function() {
        plantImage.style.display = 'none';
        plantPlaceholder.style.display = 'block';
    };
    plantImage.onload = function() {
        plantImage.style.display = 'block';
        plantPlaceholder.style.display = 'none';
    };
}

export { updatePlantImage };
