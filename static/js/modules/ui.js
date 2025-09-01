// UI-related functions migrated from main.js
import { updateCalculationIfReady } from './calculator.js';
import { updatePlantImage } from './plantGrid.js';
import { debounce } from './utils.js';

let currentPlant = 'Carrot';
let currentVariant = 'Normal';
let selectedMutations = [];

export function initializeActionButtons() {
    // Share result button
    const shareButton = document.getElementById('share-result');
    if (shareButton) {
        shareButton.addEventListener('click', async function() {
            alert('Share functionality not yet implemented in modules.');
        });
    }
    // Clear all button
    const clearAllButton = document.getElementById('clear-all');
    if (clearAllButton) {
        clearAllButton.addEventListener('click', function() {
            selectedMutations = [];
            currentVariant = 'Normal';
            currentPlant = 'Carrot';
            const weightInput = document.getElementById('plant-weight');
            if (weightInput) weightInput.value = '0.24';
            const amountInput = document.getElementById('plant-amount');
            if (amountInput) amountInput.value = '1';
            updatePlantImage('Carrot');
            updateCalculationIfReady();
        });
    }
}

export function updateVariantSelection(selectedVariant) {
    const variantLabels = document.querySelectorAll('input[name="variant"]');
    variantLabels.forEach(radio => {
        const label = radio.closest('label');
        if (label) {
            if (radio.value === selectedVariant) {
                label.classList.remove('bg-gray-700/30', 'text-gray-300');
                label.classList.add('bg-green-700/50', 'border-green-500', 'text-white');
            } else {
                label.classList.remove('bg-green-700/50', 'border-green-500', 'text-white');
                label.classList.add('bg-gray-700/30', 'text-gray-300');
            }
        }
    });
}

export function preloadPlantImages() {
    const plantButtons = document.querySelectorAll('[data-plant]');
    plantButtons.forEach(button => {
        const plantName = button.dataset.plant;
        const cropImage = button.querySelector('.crop-image');
        const cropPlaceholder = button.querySelector('.crop-placeholder');
        if (cropImage && cropPlaceholder) {
            const filename = plantName.toLowerCase().replace(/\s+/g, '-').replace(/'/g, '');
            const imagePath = `/static/img/crop-${filename}.webp`;
            cropImage.src = imagePath;
            cropImage.alt = plantName;
            cropImage.onerror = function() {
                this.style.display = 'none';
                cropPlaceholder.style.display = 'block';
            };
            cropImage.onload = function() {
                this.style.display = 'block';
                cropPlaceholder.style.display = 'none';
            };
        }
    });
}