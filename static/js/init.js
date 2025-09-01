import { state } from './modules/state.js';

function setDefaultValues() {
    const plantAmountInput = document.getElementById('plant-amount');
    const plantWeightInput = document.getElementById('plant-weight');
    if (plantAmountInput) plantAmountInput.value = '1';
    if (plantWeightInput) plantWeightInput.value = '0.24';
}

function updateCalculationIfReady() {
    if (state.currentPlant) {
        window.calculatePlantValue(state.currentPlant, state.currentVariant, state.selectedMutations, state.API_BASE);
    }
}

function updateWeightRange() {
    // ...existing logic from main.js, refactored to use state...
}

function updatePlantImage(plantName) {
    // ...existing logic from main.js, refactored to use state...
}

function initializeCalculatorForm() {
    // ...existing logic from main.js, refactored to use state and modular functions...
    setDefaultValues();
    // ...other initializations...
}

window.setDefaultValues = setDefaultValues;
window.updateCalculationIfReady = updateCalculationIfReady;
window.updateWeightRange = updateWeightRange;
window.updatePlantImage = updatePlantImage;
window.state = state;

document.addEventListener('DOMContentLoaded', () => {
    initializeCalculatorForm();
    initializePlantGrid();
    initializeMutationSelection();
    initializeBatchCalculator();
});
import { initializePlantGrid } from './modules/plantGrid.js';
import { initializeMutationSelection, initializeMutationSearch, updateMutationDisplay } from './modules/mutationSelection.js';
import { calculatePlantValue, displayResults } from './modules/calculator.js';
import { initializeBatchCalculator } from './modules/batchCalculator.js';
import { debounce, formatNumber, formatLargeNumber } from './modules/utils.js';

window.updateMutationDisplay = updateMutationDisplay;
window.displayResults = displayResults;
window.debounce = debounce;
window.formatNumber = formatNumber;
window.formatLargeNumber = formatLargeNumber;
window.calculatePlantValue = calculatePlantValue;
window.initializeMutationSearch = initializeMutationSearch;

document.addEventListener('DOMContentLoaded', () => {
    initializePlantGrid();
    initializeMutationSelection();
    initializeBatchCalculator();
    // Add any other initializations needed
});
