/**
 * Main JavaScript functionality for GrowCalculator
 */

// Global state
let selectedMutations = [];
let currentVariant = 'Normal';
let currentPlant = 'Carrot';
let allMutations = [];
let allPlants = [];
let allVariants = [];

// Batch calculator state
let batchPlants = [];
let batchRowCounter = 0;

// API endpoints
const API_BASE = '/api';

/**
 * Initialize the calculator form
 */
function initializeCalculatorForm() {
    console.log('Initializing calculator form...');
    
    // Initialize variant selection
    const variantRadios = document.querySelectorAll('input[name="variant"]');
    variantRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentVariant = this.value;
            updateCalculationIfReady();
        });
    });

    // Auto-calculate on input changes
    const weightInput = document.getElementById('plant-weight');
    const amountInput = document.getElementById('plant-amount');
    
    if (weightInput) {
        weightInput.addEventListener('input', debounce(updateCalculationIfReady, 500));
    }
    
    if (amountInput) {
        amountInput.addEventListener('input', debounce(updateCalculationIfReady, 500));
    }
    
    // Initialize plant grid functionality
    initializePlantGrid();
    
    // Initialize weight range for default plant
    updateWeightRange();
    
    // Initialize action buttons
    initializeActionButtons();
    
    // Initialize mutation selection
    initializeMutationSelection();
    
    // Trigger initial calculation
    setTimeout(() => {
        updateCalculationIfReady();
    }, 100);
    
    // Set initial plant image
    updatePlantImage('Carrot');
    
    // Set default values to prevent flash
    setDefaultValues();
}

/**
 * Set default values to prevent flash
 */
function setDefaultValues() {
    // Set default input values
    const plantAmountInput = document.getElementById('plant-amount');
    const plantWeightInput = document.getElementById('plant-weight');
    
    if (plantAmountInput) plantAmountInput.value = '1';
    if (plantWeightInput) plantWeightInput.value = '0.24';
}

/**
 * Initialize plant grid functionality
 */
function initializePlantGrid() {
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
        currentPlant = plantButton.dataset.plant;
        console.log('Selected plant:', currentPlant);
        
        // Update plant image
        updatePlantImage(currentPlant);
        
        // Update weight range first, then trigger calculation when complete
        updateWeightRange().then(() => {
            console.log('Weight range update complete, now triggering calculation...');
            // Now that weight range is updated, trigger calculation
            updateCalculationIfReady();
        }).catch(error => {
            console.error('Error updating weight range:', error);
            // Still try to calculate even if weight range fails
            updateCalculationIfReady();
        });
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
        currentPlant = 'Carrot';
        
        // Update plant image for default plant
        updatePlantImage('Carrot');
    } else {
        console.warn('Default plant (Carrot) not found');
    }
    
    // Preload all plant images
    preloadPlantImages();
}

/**
 * Initialize action buttons
 */
function initializeActionButtons() {
    console.log('Initializing action buttons...');
    
    // Share result button
    const shareButton = document.getElementById('share-result');
    if (shareButton) {
        shareButton.addEventListener('click', async function() {
            console.log('Share result button clicked');
            
            // Check if we have calculation results to share
            if (!currentPlant) {
                alert('Please select a plant before sharing results.');
                return;
            }
            
            // Check if we have any calculation results
            const currentResultValue = document.getElementById('result-value');
            if (!currentResultValue || currentResultValue.textContent.includes('≈$0') || currentResultValue.textContent === '🌿') {
                alert('Please calculate a plant value before sharing results.');
                return;
            }
            
            // Get current calculation results
            const currentFinalSheckles = document.getElementById('final-sheckles');
            const currentTotalValue = document.getElementById('total-value');
            
            // Get additional calculation details
            const totalMultiplier = document.getElementById('total-multiplier')?.textContent || 'x1';
            const mutationBreakdown = document.getElementById('mutation-breakdown')?.textContent || 'Default';
            const weightMin = document.getElementById('weight-min')?.textContent || '0.17';
            const weightMax = document.getElementById('weight-max')?.textContent || '0.38';
            
            // Create share data
            const shareData = {
                plant: currentPlant,
                variant: currentVariant,
                mutations: selectedMutations,
                weight: document.getElementById('plant-weight')?.value || '0.24',
                amount: document.getElementById('plant-amount')?.value || '1',
                result_value: currentResultValue?.textContent || '',
                final_sheckles: currentFinalSheckles?.textContent || '',
                total_value: currentTotalValue?.textContent || '',
                total_multiplier: totalMultiplier,
                mutation_breakdown: mutationBreakdown,
                weight_min: weightMin,
                weight_max: weightMax,
                created_at: new Date().toISOString(),
                expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
            };
            
            // Store share data in database via API
            try {
                const response = await fetch('/api/share', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(shareData)
                });

                if (!response.ok) {
                    throw new Error('Failed to create share');
                }

                const result = await response.json();
                if (result.success && result.data) {
                    // Use the share_id returned from the API response
                    const shareId = result.data.share_id;
                    // Redirect to share page
                    window.open(`/share/${shareId}`, '_blank');
                } else {
                    alert('Failed to create share: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error creating share:', error);
                alert('Failed to create share. Please try again.');
            }
        });
    } else {
        console.warn('Share result button not found');
    }
    
    // Clear all button
    const clearAllButton = document.getElementById('clear-all');
    if (clearAllButton) {
        clearAllButton.addEventListener('click', function() {
            console.log('Clear all button clicked');
            
            // Clear mutations
            selectedMutations = [];
            const mutationCheckboxes = document.querySelectorAll('input[type="checkbox"][data-mutation]');
            mutationCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
                const label = checkbox.closest('label');
                if (label) {
                    label.classList.remove('bg-green-700/50', 'border-green-500', 'text-white');
                    label.classList.add('bg-gray-700/30', 'text-gray-300');
                }
            });
            
            // Reset variant to Normal
            currentVariant = 'Normal';
            const normalRadio = document.querySelector('input[value="Normal"]');
            if (normalRadio) {
                normalRadio.checked = true;
                // Update variant visual state
                const variantRadios = document.querySelectorAll('input[name="variant"]');
                variantRadios.forEach(radio => {
                    const label = radio.closest('label');
                    if (label) {
                        if (radio.checked) {
                            label.classList.remove('bg-gray-700/30', 'text-gray-300');
                            label.classList.add('bg-green-700/50', 'border-green-500', 'text-white');
                        } else {
                            label.classList.remove('bg-green-700/50', 'border-green-500', 'text-white');
                            label.classList.add('bg-gray-700/30', 'text-gray-300');
                        }
                    }
                });
            }
            
            // Reset plant selection back to Carrot
            currentPlant = 'Carrot';
            const plantGrid = document.getElementById('plant-grid');
            if (plantGrid) {
                // Remove selection from all plants
                const allPlantButtons = plantGrid.querySelectorAll('[data-plant]');
                allPlantButtons.forEach(button => {
                    button.classList.remove('bg-green-800', 'border-green-600', 'ring-2', 'ring-green-400');
                    button.classList.add('bg-gray-700', 'border-gray-600');
                    button.setAttribute('aria-pressed', 'false');
                });
                
                // Select Carrot
                const carrotButton = plantGrid.querySelector('[data-plant="Carrot"]');
                if (carrotButton) {
                    carrotButton.classList.remove('bg-gray-700', 'border-gray-600');
                    carrotButton.classList.add('bg-green-800', 'border-green-600', 'ring-2', 'ring-green-400');
                    carrotButton.setAttribute('aria-pressed', 'true');
                }
            }
            
            // Reset weight to Carrot's base weight
            const weightInput = document.getElementById('plant-weight');
            if (weightInput) {
                weightInput.value = '0.24';
            }
            
            // Reset plant amount to 1
            const amountInput = document.getElementById('plant-amount');
            if (amountInput) {
                amountInput.value = '1';
            }
            
            console.log('Cleared all selections, reset to Carrot');
            
            // Update plant image back to Carrot
            updatePlantImage('Carrot');
            
            // Update weight range and trigger calculation
            updateWeightRange().then(() => {
                updateCalculationIfReady();
            });
        });
    } else {
        console.warn('Clear all button not found');
    }
}

/**
 * Update variant selection styling
 */
function updateVariantSelection(selectedVariant) {
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



/**
 * Initialize mutation selection functionality
 */
function initializeMutationSelection() {
    const mutationCheckboxes = document.querySelectorAll('input[type="checkbox"][data-mutation]');
    const variantRadios = document.querySelectorAll('input[name="variant"]');
    
    console.log('Initializing mutation selection...');
    console.log('Found mutation checkboxes:', mutationCheckboxes.length);
    console.log('Found variant radios:', variantRadios.length);
    
    // Add scrollbar to mutations container if it exists
    // Look for the mutations section by finding the h3 with "Environmental Mutations" text
    const mutationsHeading = Array.from(document.querySelectorAll('h3')).find(h3 => 
        h3.textContent.includes('Environmental Mutations')
    );
    
    console.log('Found mutations heading:', mutationsHeading);
    
    if (mutationsHeading) {
        const mutationsContainer = mutationsHeading.closest('.bg-gray-800');
        console.log('Found mutations container:', mutationsContainer);
        
        if (mutationsContainer) {
            // Find the grid container within the mutations section
            const mutationsGrid = mutationsContainer.querySelector('.grid');
            console.log('Found mutations grid:', mutationsGrid);
            
            if (mutationsGrid) {
                // Force the scrollbar to appear by setting a smaller max height
                mutationsGrid.style.maxHeight = 'calc(6 * 2.5rem + 1rem)'; // Reduced to 6 rows to ensure scrollbar appears
                mutationsGrid.style.overflowY = 'auto';
                mutationsGrid.style.scrollbarWidth = 'thin';
                mutationsGrid.style.scrollbarColor = '#10b981 #2d3748';
                
                // Custom scrollbar styling for webkit browsers
                mutationsGrid.style.setProperty('--scrollbar-thumb', '#10b981');
                mutationsGrid.style.setProperty('--scrollbar-track', '#2d3748');
                
                // Add custom scrollbar CSS with a unique identifier and prevent conflicts
                const existingStyle = document.getElementById('mutations-scrollbar-style');
                if (existingStyle) {
                    existingStyle.remove();
                }
                
                const style = document.createElement('style');
                style.id = 'mutations-scrollbar-style';
                style.textContent = `
                    .mutations-scrollable::-webkit-scrollbar {
                        width: 6px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-track {
                        background: #2d3748 !important;
                        border-radius: 3px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-thumb {
                        background: #10b981 !important;
                        border-radius: 3px !important;
                        min-height: 40px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-thumb:hover {
                        background: #059669 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button {
                        background: #10b981 !important;
                        height: 12px !important;
                        border-radius: 2px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:hover {
                        background: #059669 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:single-button:start {
                        border-radius: 2px 2px 0 0 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:single-button:end {
                        border-radius: 0 0 2px 2px !important;
                    }
                `;
                document.head.appendChild(style);
                
                // Add the class for webkit scrollbar styling
                mutationsGrid.classList.add('mutations-scrollable');
                
                // Force a reflow to ensure styles are applied
                mutationsGrid.offsetHeight;
                
                // Add a MutationObserver to ensure scrollbar styling persists
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                            // Re-apply scrollbar styling if it gets removed
                            if (!mutationsGrid.style.overflowY || mutationsGrid.style.overflowY !== 'auto') {
                                mutationsGrid.style.maxHeight = 'calc(6 * 2.5rem + 1rem)';
                                mutationsGrid.style.overflowY = 'auto';
                                mutationsGrid.style.scrollbarWidth = 'thin';
                                mutationsGrid.style.scrollbarColor = '#10b981 #2d3748';
                            }
                        }
                    });
                });
                
                observer.observe(mutationsGrid, { attributes: true, attributeFilter: ['style'] });
                
                console.log('Scrollbar added to mutations grid with exact plant grid styling');
                console.log('Grid max height:', mutationsGrid.style.maxHeight);
                console.log('Grid overflow:', mutationsGrid.style.overflowY);
                console.log('Grid classes:', mutationsGrid.className);
                console.log('MutationObserver added to maintain scrollbar styling');
            } else {
                console.error('Mutations grid not found within container');
            }
        } else {
            console.error('Mutations container not found');
        }
    } else {
        console.error('Environmental Mutations heading not found');
    }
    
    // Initialize mutation search functionality
    console.log('About to initialize mutation search...');
    setTimeout(() => {
        initializeMutationSearch();
    }, 100); // Small delay to ensure DOM is ready
    
    // Handle mutation checkboxes
    mutationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.closest('label');
            if (this.checked) {
                label.classList.remove('bg-gray-700/30', 'text-gray-300');
                label.classList.add('bg-green-700/50', 'border-green-500', 'text-white');
                selectedMutations.push(this.dataset.mutation);
                console.log('Added mutation:', this.dataset.mutation);
            } else {
                label.classList.remove('bg-green-700/50', 'border-green-500', 'text-white');
                label.classList.add('bg-gray-700/30', 'text-gray-300');
                const index = selectedMutations.indexOf(this.dataset.mutation);
                if (index > -1) {
                    selectedMutations.splice(index, 1);
                    console.log('Removed mutation:', this.dataset.mutation);
                }
            }
            console.log('Current mutations:', selectedMutations);
            updateCalculationIfReady();
        });
    });
    
    // Handle variant radios
    variantRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log('Variant changed to:', this.value);
            
            // Update visual state for all variant labels
            variantRadios.forEach(r => {
                const label = r.closest('label');
                if (r.checked) {
                    label.classList.remove('bg-gray-700/30', 'text-gray-300');
                    label.classList.add('bg-green-700/50', 'border-green-500', 'text-white');
                } else {
                    label.classList.remove('bg-green-700/50', 'border-green-500', 'text-white');
                    label.classList.add('bg-gray-700/30', 'text-gray-300');
                }
            });
            
            currentVariant = this.value;
            updateCalculationIfReady();
        });
    });
}



/**
 * Initialize mutation search functionality
 */
function initializeMutationSearch() {
    const searchInput = document.getElementById('mutation-search');
    
    if (!searchInput) {
        console.warn('Mutation search input not found');
        return;
    }
    
    console.log('Initializing mutation search...');
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        console.log('Searching for mutations containing:', searchTerm);
        
        // Get all mutation labels dynamically each time to ensure we have the latest
        const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
        console.log('Found', mutationLabels.length, 'mutation checkboxes to search through');
        
        let visibleCount = 0;
        mutationLabels.forEach(checkbox => {
            const label = checkbox.closest('label');
            if (!label) {
                console.warn('No label found for checkbox:', checkbox);
                return;
            }
            
            const mutationName = checkbox.dataset.mutation.toLowerCase();
            console.log('Checking mutation:', mutationName, 'against search term:', searchTerm);
            
            if (mutationName.includes(searchTerm)) {
                label.style.display = 'flex';
                visibleCount++;
            } else {
                label.style.display = 'none';
            }
        });
        
        console.log('Found', visibleCount, 'visible mutations');
    });
    
    // Clear search when input is cleared
    searchInput.addEventListener('change', function() {
        if (this.value === '') {
            const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
            mutationLabels.forEach(checkbox => {
                const label = checkbox.closest('label');
                if (label) {
                    label.style.display = 'flex';
                }
            });
            console.log('Search cleared, showing all mutations');
        }
    });
    
    // Also clear on keyup for better responsiveness
    searchInput.addEventListener('keyup', function() {
        if (this.value === '') {
            const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
            mutationLabels.forEach(checkbox => {
                const label = checkbox.closest('label');
                if (label) {
                    label.style.display = 'flex';
                }
            });
        }
    });
    
    console.log('Mutation search functionality initialized successfully');
}

/**
 * Toggle mutation selection
 */
function toggleMutation(mutationName) {
    const index = selectedMutations.indexOf(mutationName);
    
    if (index > -1) {
        selectedMutations.splice(index, 1);
    } else {
        selectedMutations.push(mutationName);
    }
    
    updateMutationDisplay();
    updateCalculationIfReady();
}

/**
 * Update mutation display
 */
function updateMutationDisplay() {
    // Update button states
    const mutationButtons = document.querySelectorAll('.mutation-chip');
    mutationButtons.forEach(button => {
        const mutation = button.getAttribute('data-mutation');
        if (selectedMutations.includes(mutation)) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });

    // Update selected mutations list
    const selectedDiv = document.getElementById('selected-mutations');
    const mutationList = document.getElementById('mutation-list');
    
    if (selectedDiv && mutationList) {
        if (selectedMutations.length > 0) {
            selectedDiv.classList.remove('hidden');
            mutationList.innerHTML = selectedMutations.map(mutation => 
                `<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-sm">${mutation}</span>`
            ).join('');
        } else {
            selectedDiv.classList.add('hidden');
        }
    }
}



/**
 * Calculate plant value
 */
async function calculatePlantValue() {
    const weightInput = document.getElementById('plant-weight');
    const amountInput = document.getElementById('plant-amount');
    
    if (!weightInput || !amountInput) return;

    const plantName = currentPlant;
    const weight = parseFloat(weightInput.value);
    const amount = parseInt(amountInput.value);

    console.log('Calculating for:', plantName, weight, amount, selectedMutations);

    if (!plantName || !weight || weight <= 0 || !amount || amount <= 0) {
        console.log('Invalid inputs, hiding results');
        hideResults();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                plant_name: plantName,
                variant: currentVariant,
                weight: weight,
                mutations: selectedMutations,
                plant_amount: amount
            })
        });

        if (!response.ok) {
            throw new Error('Calculation failed');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Calculation error:', error);
        hideResults();
    }
}

/**
 * Display calculation results
 */
function displayResults(result) {
    // The results are always visible in our new layout, just update them

    // Get current values for animation
    const currentResultValue = document.getElementById('result-value');
    const currentTotalValue = document.getElementById('total-value');
    const currentResultSheckles = document.getElementById('result-sheckles');
    const currentFinalSheckles = document.getElementById('final-sheckles');
    const currentTotalSheckles = document.getElementById('total-sheckles');
    
    // Extract current numeric values for smooth animation
    let currentDollarValue = 0;
    let currentTotalDollarValue = 0;
    let currentShecklesValue = 0;
    let currentFinalShecklesValue = 0;
    let currentTotalShecklesValue = 0;
    
    if (currentResultValue) {
        const currentText = currentResultValue.textContent;
        const match = currentText.match(/\$([0-9,]+)/);
        if (match) {
            currentDollarValue = parseInt(match[1].replace(/,/g, ''));
        }
    }
    
    if (currentTotalValue) {
        const currentText = currentTotalValue.textContent;
        const match = currentText.match(/\$([0-9,]+)/);
        if (match) {
            currentTotalDollarValue = parseInt(match[1].replace(/,/g, ''));
        }
    }
    
    if (currentResultSheckles) {
        const currentText = currentResultSheckles.textContent;
        const match = currentText.match(/\(([0-9,.]+)\)/);
        if (match) {
            currentShecklesValue = parseFloat(match[1].replace(/,/g, ''));
        }
    }
    
    if (currentFinalSheckles) {
        const currentText = currentFinalSheckles.textContent;
        const match = currentText.match(/([0-9,.]+)/);
        if (match) {
            currentFinalShecklesValue = parseFloat(match[1].replace(/,/g, ''));
        }
    }
    
    if (currentTotalSheckles) {
        const currentText = currentTotalSheckles.textContent;
        const match = currentText.match(/\(([0-9,.]+)/);
        if (match) {
            currentTotalShecklesValue = parseFloat(match[1].replace(/,/g, ''));
        }
    }

    // Update result displays with safety checks (non-animated elements)
    const elementsToUpdate = [
        { id: 'result-title', text: `${result.plant_name} | ${result.weight}kg | would sell around:` },
        { id: 'total-multiplier', text: `x${result.mutation_multiplier.toFixed(2)}` },
        { id: 'plant-name', text: result.plant_name },
        { id: 'weight-display', text: result.weight },
        { id: 'multiplier-display', text: `x${result.mutation_multiplier.toFixed(2)}` },
        { id: 'plant-count', text: result.plant_amount }
    ];
    
    elementsToUpdate.forEach(({ id, text }) => {
        updateElement(id, text);
    });
    
    // Animate the main dollar value
    if (currentResultValue) {
        animateNumber(currentResultValue, currentDollarValue, result.final_value, 500, true);
    }
    
    // Animate the total dollar value
    if (currentTotalValue) {
        animateNumber(currentTotalValue, currentTotalDollarValue, result.total_value, 500, false);
    }
    
    // Animate result-sheckles
    if (currentResultSheckles) {
        animateSheckles(currentResultSheckles, currentShecklesValue, result.final_value);
    }
    
    // Animate final-sheckles in the summary text
    if (currentFinalSheckles) {
        // Update instantly without animation for the summary text, using abbreviated format
        const formattedValue = formatLargeNumber(result.final_value);
        currentFinalSheckles.textContent = formattedValue;
    }
    
    // Animate total-sheckles
    if (currentTotalSheckles) {
        animateSheckles(currentTotalSheckles, currentTotalShecklesValue, result.total_value, 500, true);
    }
    
    // Show/hide total value section based on plant amount
    const totalValueSection = document.getElementById('total-value-section');
    if (totalValueSection) {
        if (result.plant_amount > 1) {
            totalValueSection.classList.remove('hidden');
        } else {
            totalValueSection.classList.add('hidden');
        }
    }

    // Update mutation breakdown
    const breakdownSpan = document.getElementById('mutation-breakdown');
    if (breakdownSpan) {
        if (result.mutations.length > 0) {
            breakdownSpan.textContent = `Mutations: ${result.mutations.join(', ')}`;
        } else {
            breakdownSpan.textContent = 'Default';
        }
    }
}

/**
 * Hide calculation results
 */
function hideResults() {
         // In our new layout, we don't hide results, just reset to defaults
     updateElement('result-title', 'Select a plant to calculate');
     const resultValueElement = document.getElementById('result-value');
     if (resultValueElement) {
         resultValueElement.innerHTML = `<img src="/static/img/currency.png" alt="Currency" class="w-8 h-8 inline-block mr-0">= $0`;
     }
    
    // Update result-sheckles separately since it's nested
    const resultSheckles = document.getElementById('result-sheckles');
    if (resultSheckles) {
        resultSheckles.textContent = '(0.00)';
    }
}

/**
 * Update weight range display when plant changes
 */
async function updateWeightRange() {
    const weightRangeDiv = document.getElementById('weight-range');
    const weightMinSpan = document.getElementById('weight-min');
    const weightMaxSpan = document.getElementById('weight-max');
    
    if (!weightRangeDiv || !weightMinSpan || !weightMaxSpan) {
        return Promise.resolve();
    }
    
    const plantName = currentPlant;
    
    if (!plantName) {
        weightRangeDiv.classList.add('hidden');
        return Promise.resolve();
    }
    
    try {
        const response = await fetch(`${API_BASE}/weight-range/${encodeURIComponent(plantName)}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch weight range');
        }
        
        const weightRange = await response.json();
        
        // Update the display
        weightMinSpan.textContent = weightRange.min;
        weightMaxSpan.textContent = weightRange.max;
        weightRangeDiv.classList.remove('hidden');
        
        // Also update the weight input to the base weight
        const weightInput = document.getElementById('plant-weight');
        if (weightInput) {
            weightInput.value = weightRange.base;
        }
        
        console.log('Weight range updated for', plantName, 'base weight:', weightRange.base);
        
    } catch (error) {
        console.error('Weight range error:', error);
        weightRangeDiv.classList.add('hidden');
    }
    
    // Always return a resolved promise
    return Promise.resolve();
}

/**
 * Update plant image when a plant is selected
 */
function updatePlantImage(plantName) {
    const plantEmojiContainer = document.getElementById('plant-emoji');
    if (!plantEmojiContainer) return;
    
    const plantImage = document.getElementById('plant-image');
    const plantPlaceholder = document.getElementById('plant-placeholder');
    
    if (!plantImage || !plantPlaceholder) return;
    
    // Convert plant name to filename format (lowercase, replace spaces with hyphens, remove apostrophes)
    const filename = plantName.toLowerCase().replace(/\s+/g, '-').replace(/'/g, '');
    const imagePath = `/static/img/crop-${filename}.webp`;
    
    // Set the image source
    plantImage.src = imagePath;
    plantImage.alt = plantName;
    
    // Handle image load errors by showing placeholder
    plantImage.onerror = function() {
        console.warn(`Image not found for ${plantName}, using fallback placeholder`);
        plantImage.style.display = 'none';
        plantPlaceholder.style.display = 'block';
    };
    
    // Handle successful image load
    plantImage.onload = function() {
        console.log(`Successfully loaded image for ${plantName}`);
        plantImage.style.display = 'block';
        plantPlaceholder.style.display = 'none';
    };
}

/**
 * Preload all plant images for better performance
 */
function preloadPlantImages() {
    const plantButtons = document.querySelectorAll('[data-plant]');
    plantButtons.forEach(button => {
        const plantName = button.dataset.plant;
        const cropImage = button.querySelector('.crop-image');
        const cropPlaceholder = button.querySelector('.crop-placeholder');
        
        if (cropImage && cropPlaceholder) {
            // Convert plant name to filename format (lowercase, replace spaces with hyphens, remove apostrophes)
            const filename = plantName.toLowerCase().replace(/\s+/g, '-').replace(/'/g, '');
            const imagePath = `/static/img/crop-${filename}.webp`;
            
            // Set the image source
            cropImage.src = imagePath;
            cropImage.alt = plantName;
            
            // Handle image load errors by showing fallback placeholder image
            cropImage.onerror = function() {
                console.warn(`Image not found for ${plantName}, using fallback placeholder`);
                this.style.display = 'none';
                cropPlaceholder.style.display = 'block';
            };
            
            // Handle successful image load
            cropImage.onload = function() {
                console.log(`Successfully loaded image for ${plantName}`);
                this.style.display = 'block';
                cropPlaceholder.style.display = 'none';
            };
        }
    });
}

/**
 * Update calculation if inputs are ready
 */
function updateCalculationIfReady() {
    console.log('updateCalculationIfReady called');
    console.log('Current plant:', currentPlant);
    console.log('Current variant:', currentVariant);
    console.log('Selected mutations:', selectedMutations);
    
    if (currentPlant) {
        console.log('Triggering calculation...');
        calculatePlantValue();
    } else {
        console.log('No plant selected, skipping calculation');
    }
}

/**
 * Initialize mutation calculator (for mutation-calculator page)
 */
function initializeMutationCalculator() {
    if (!document.getElementById('selected-mutations-panel')) return;

    const mutationButtons = document.querySelectorAll('.mutation-btn');
    const selectedMutationsList = document.getElementById('selected-mutations-list');
    const multiplierDisplay = document.getElementById('total-multiplier-display');
    const breakdownDisplay = document.getElementById('multiplier-breakdown');

    mutationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mutation = this.getAttribute('data-mutation');
            toggleMutationInCalculator(mutation);
            updateMutationCalculatorDisplay();
        });
    });

    // Clear all button
    const clearAllButton = document.getElementById('clear-all-mutations');
    if (clearAllButton) {
        clearAllButton.addEventListener('click', function() {
            selectedMutations = [];
            updateMutationCalculatorDisplay();
        });
    }

    // Random mutations button
    const randomButton = document.getElementById('random-mutations');
    if (randomButton) {
        randomButton.addEventListener('click', function() {
            const allMutationNames = Array.from(mutationButtons).map(btn => btn.getAttribute('data-mutation'));
            selectedMutations = getRandomMutations(allMutationNames, 3);
            updateMutationCalculatorDisplay();
        });
    }

    function toggleMutationInCalculator(mutationName) {
        const index = selectedMutations.indexOf(mutationName);
        
        if (index > -1) {
            selectedMutations.splice(index, 1);
        } else {
            selectedMutations.push(mutationName);
        }
    }

    function updateMutationCalculatorDisplay() {
        // Update button states
        mutationButtons.forEach(button => {
            const mutation = button.getAttribute('data-mutation');
            if (selectedMutations.includes(mutation)) {
                button.classList.add('bg-purple-600', 'text-white');
                button.classList.remove('bg-gray-100', 'text-gray-700');
            } else {
                button.classList.remove('bg-purple-600', 'text-white');
                button.classList.add('bg-gray-100', 'text-gray-700');
            }
        });

        // Update selected mutations list
        if (selectedMutationsList) {
            if (selectedMutations.length > 0) {
                selectedMutationsList.innerHTML = selectedMutations.map(mutation => 
                    `<span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">${mutation}</span>`
                ).join('');
            } else {
                selectedMutationsList.innerHTML = '<span class="text-gray-500 text-sm">No mutations selected</span>';
            }
        }

        // Calculate and display multiplier
        calculateMutationMultiplier();
    }

    async function calculateMutationMultiplier() {
        try {
            const response = await fetch(`${API_BASE}/mutation-multiplier`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(selectedMutations)
            });

            if (!response.ok) {
                throw new Error('Failed to calculate multiplier');
            }

            const result = await response.json();
            
            if (multiplierDisplay) {
                multiplierDisplay.textContent = `x${result.multiplier.toFixed(2)}`;
            }
            
            if (breakdownDisplay) {
                if (selectedMutations.length > 0) {
                    breakdownDisplay.textContent = `Base: 1.00 + Mutations: ${(result.multiplier - 1).toFixed(2)}`;
                } else {
                    breakdownDisplay.textContent = 'Base: 1.00';
                }
            }

            // Update example values
            updateExampleValues(result.multiplier);
            updateStatistics(result);

        } catch (error) {
            console.error('Multiplier calculation error:', error);
        }
    }

    function updateExampleValues(multiplier) {
        const carrotValue = document.getElementById('carrot-value');
        const strawberryValue = document.getElementById('strawberry-value');
        
        if (carrotValue) {
            const baseCarrotValue = 18;
            carrotValue.textContent = `$${formatNumber(Math.round(baseCarrotValue * multiplier))}`;
        }
        
        if (strawberryValue) {
            const baseStrawberryValue = 90000;
            strawberryValue.textContent = `$${formatNumber(Math.round(baseStrawberryValue * multiplier))}`;
        }
    }

    function updateStatistics(result) {
        const totalCount = document.getElementById('total-mutations-count');
        const averageValue = document.getElementById('average-mutation-value');
        const highestMutation = document.getElementById('highest-mutation');
        
        if (totalCount) {
            totalCount.textContent = result.total_mutations;
        }
        
        if (averageValue && result.total_mutations > 0) {
            averageValue.textContent = ((result.multiplier - 1) / result.total_mutations + 1).toFixed(2);
        }
        
        if (highestMutation && selectedMutations.length > 0) {
            // This would need mutation data to determine the highest
            highestMutation.textContent = selectedMutations[0]; // Placeholder
        }
    }
}

/**
 * Utility Functions
 */

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format large numbers into readable abbreviations
 */
function formatLargeNumber(num) {
    if (num >= 1e21) {
        return (num / 1e21).toFixed(2) + ' Sextillion';
    } else if (num >= 1e18) {
        return (num / 1e18).toFixed(2) + ' Quintillion';
    } else if (num >= 1e15) {
        return (num / 1e15).toFixed(2) + ' Quadrillion';
    } else if (num >= 1e12) {
        return (num / 1e12).toFixed(2) + ' Trillion';
    } else if (num >= 1e9) {
        return (num / 1e9).toFixed(2) + ' Billion';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(2) + ' Million';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    } else {
        return num.toFixed(2);
    }
}

/**
 * Animate number counting smoothly
 */
function animateNumber(element, startValue, endValue, duration = 500, isResultValue = false) {
    if (!element) return;
    
    const start = performance.now();
    const difference = endValue - startValue;
    
    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = startValue + (difference * easeOutQuart);
        
        // Format the number with commas
        const formattedValue = formatNumber(Math.round(currentValue));
        
                 if (isResultValue) {
             element.innerHTML = `<img src="/static/img/currency.png" alt="Currency" class="w-8 h-8 inline-block mr-0">= $${formattedValue}`;
         } else {
             element.textContent = `💰 $${formattedValue}`;
         }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

/**
 * Animate sheckles counting smoothly
 */
function animateSheckles(element, startValue, endValue, duration = 500, includeSheckles = false, isFinalSheckles = false) {
    if (!element) return;
    
    const start = performance.now();
    const difference = endValue - startValue;
    
    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = startValue + (difference * easeOutQuart);
        
        // Format the number with commas and decimal places
        const integerPart = Math.floor(currentValue);
        const decimalPart = (currentValue % 1).toFixed(2).substring(1);
        const formattedInteger = formatNumber(integerPart);
        
        if (isFinalSheckles) {
            // For final-sheckles, don't include parentheses
            element.textContent = `${formattedInteger}${decimalPart}`;
        } else if (includeSheckles) {
            element.textContent = `(${formattedInteger}${decimalPart} Sheckles)`;
        } else {
            element.textContent = `(${formattedInteger}${decimalPart})`;
        }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Update element text content safely
function updateElement(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    } else {
        console.warn(`Element with id '${id}' not found`);
    }
}

// Debounce function for input events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Generate unique share ID
function generateShareId() {
    return 'share_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Get random mutations
function getRandomMutations(allMutations, count) {
    const shuffled = allMutations.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

// Load predefined mutation combo
function loadCombo(mutations) {
    selectedMutations = [...mutations];
    if (typeof updateMutationCalculatorDisplay === 'function') {
        updateMutationCalculatorDisplay();
    } else {
        updateMutationDisplay();
        updateCalculationIfReady();
    }
}

// ========================================
// TAB SYSTEM AND BATCH CALCULATOR
// ========================================

/**
 * Initialize the tab system
 */
function initializeTabSystem() {
    const singleTab = document.getElementById('single-calculator-tab');
    const batchTab = document.getElementById('batch-calculator-tab');
    const singleContent = document.getElementById('single-calculator-content');
    const batchContent = document.getElementById('batch-calculator-content');
    
    if (!singleTab || !batchTab || !singleContent || !batchContent) {
        console.warn('Tab system elements not found');
        return;
    }
    
    // Single calculator tab click
    singleTab.addEventListener('click', function() {
        singleTab.classList.remove('bg-gray-600', 'text-gray-300');
        singleTab.classList.add('bg-green-600', 'text-white');
        batchTab.classList.remove('bg-green-600', 'text-white');
        batchTab.classList.add('bg-gray-600', 'text-gray-300');
        
        singleContent.classList.remove('hidden');
        batchContent.classList.add('hidden');
    });
    
    // Batch calculator tab click
    batchTab.addEventListener('click', function() {
        showComingSoonPopup();
    });
}

/**
 * Show "Coming Soon" popup for batch calculator
 */
function showComingSoonPopup() {
    // Create popup overlay
    const popup = document.createElement('div');
    popup.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
    popup.id = 'coming-soon-popup';
    
    popup.innerHTML = `
        <div class="bg-gray-800 p-8 rounded-lg shadow-xl max-w-md w-full mx-4 border border-gray-600">
            <div class="text-center">
                <div class="text-6xl mb-4">🚀</div>
                <h3 class="text-2xl font-bold mb-4 text-green-400">Coming Soon!</h3>
                <p class="text-lg text-gray-300 mb-6">
                    The <strong>Batch Calculator</strong> feature is currently under development.
                </p>
                <p class="text-sm text-gray-400 mb-6">
                    Soon you'll be able to calculate multiple plants at once with quantities, 
                    real-time updates, and batch sharing!
                </p>
                <button class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200 w-full">
                    Got it!
                </button>
            </div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(popup);
    
    // Close popup when clicking the button
    const closeButton = popup.querySelector('button');
    closeButton.addEventListener('click', () => {
        popup.remove();
    });
    
    // Close popup when clicking outside
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.remove();
        }
    });
    
    // Close popup with Escape key
    document.addEventListener('keydown', function closeOnEscape(e) {
        if (e.key === 'Escape') {
            popup.remove();
            document.removeEventListener('keydown', closeOnEscape);
        }
    });
}

/**
 * Add initial batch plant row
 */
function addInitialBatchRow() {
    addBatchPlantRow();
}

/**
 * Add a new plant row to the batch calculator
 */
function addBatchPlantRow() {
    batchRowCounter++;
    const rowId = `batch-row-${batchRowCounter}`;
    
    // Create plant row HTML
    const plantRow = document.createElement('div');
    plantRow.className = 'bg-gray-700 p-4 rounded-lg border border-gray-600';
    plantRow.id = rowId;
    
    plantRow.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3 items-end">
            <!-- Plant Selector -->
            <div>
                <label class="block text-sm mb-1 text-gray-300">Plant</label>
                <select class="batch-plant-select w-full p-2 rounded bg-gray-600 border border-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-green-500">
                    <option value="">Select Plant</option>
                    ${allPlants.map(plant => `<option value="${plant.name}">${plant.name}</option>`).join('')}
                </select>
            </div>
            
            <!-- Variant Selector -->
            <div>
                <label class="block text-sm mb-1 text-gray-300">Variant</label>
                <select class="batch-variant-select w-full p-2 rounded bg-gray-600 border border-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-green-500">
                    ${allVariants.map(variant => `<option value="${variant.name}">${variant.name} (x${variant.multiplier})</option>`).join('')}
                </select>
            </div>
            
            <!-- Weight Input -->
            <div>
                <label class="block text-sm mb-1 text-gray-300">Weight (kg)</label>
                <input type="number" step="0.01" min="0" class="batch-weight-input w-full p-2 rounded bg-gray-600 border border-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="0.00">
            </div>
            
            <!-- Quantity Input -->
            <div>
                <label class="block text-sm mb-1 text-gray-300">Qty</label>
                <input type="number" min="1" value="1" class="batch-quantity-input w-full p-2 rounded bg-gray-600 border border-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-green-500">
            </div>
            
            <!-- Mutations -->
            <div>
                <label class="block text-sm mb-1 text-gray-300">Mutations</label>
                <select class="batch-mutations-select w-full p-2 rounded bg-gray-600 border border-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-green-500" multiple>
                    ${allMutations.map(mutation => `<option value="${mutation.name}">${mutation.name} (+${mutation.value_multi - 1})</option>`).join('')}
                </select>
            </div>
            
            <!-- Remove Button -->
            <div>
                <button class="remove-batch-row bg-red-600 hover:bg-red-700 px-3 py-2 rounded text-white font-medium transition-colors duration-200" data-row-id="${rowId}">
                    🗑️ Remove
                </button>
            </div>
        </div>
        
        <!-- Individual Result Display -->
        <div class="mt-3 p-3 bg-gray-800 rounded border-l-4 border-blue-500 hidden batch-result-display">
            <div class="text-sm text-gray-300">
                <span class="font-medium">Result:</span> 
                <span class="text-green-400 font-bold batch-result-value">0 sheckles</span>
                <span class="text-blue-400 ml-2">(per plant)</span>
            </div>
        </div>
    `;
    
    // Add event listeners
    const plantSelect = plantRow.querySelector('.batch-plant-select');
    const variantSelect = plantRow.querySelector('.batch-variant-select');
    const weightInput = plantRow.querySelector('.batch-weight-input');
    const quantityInput = plantRow.querySelector('.batch-quantity-input');
    const mutationsSelect = plantRow.querySelector('.batch-mutations-select');
    const removeBtn = plantRow.querySelector('.remove-batch-row');
    
    // Plant selection change
    plantSelect.addEventListener('change', function() {
        updateBatchRowCalculation(rowId);
    });
    
    // Variant selection change
    variantSelect.addEventListener('change', function() {
        updateBatchRowCalculation(rowId);
    });
    
    // Weight input change
    weightInput.addEventListener('input', debounce(() => {
        updateBatchRowCalculation(rowId);
    }, 500));
    
    // Quantity input change
    quantityInput.addEventListener('input', debounce(() => {
        updateBatchRowCalculation(rowId);
    }, 500));
    
    // Mutations selection change
    mutationsSelect.addEventListener('change', function() {
        updateBatchRowCalculation(rowId);
    });
    
    // Remove row button
    removeBtn.addEventListener('click', function() {
        removeBatchRow(rowId);
    });
    
    // Add to container
    const container = document.getElementById('batch-plant-rows');
    if (container) {
        container.appendChild(plantRow);
        
        // Add to batch plants array
        batchPlants.push({
            id: rowId,
            plant: '',
            variant: 'Normal',
            weight: 0,
            quantity: 1,
            mutations: [],
            result: 0
        });
    }
}

/**
 * Remove a batch plant row
 */
function removeBatchRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
        
        // Remove from batch plants array
        batchPlants = batchPlants.filter(plant => plant.id !== rowId);
        
        // Update batch calculations
        updateBatchCalculations();
    }
}

/**
 * Update calculation for a specific batch row
 */
async function updateBatchRowCalculation(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;
    
    const plantSelect = row.querySelector('.batch-plant-select');
    const variantSelect = row.querySelector('.batch-variant-select');
    const weightInput = row.querySelector('.batch-weight-input');
    const quantityInput = row.querySelector('.batch-quantity-input');
    const mutationsSelect = row.querySelector('.batch-mutations-select');
    const resultDisplay = row.querySelector('.batch-result-display');
    const resultValue = row.querySelector('.batch-result-value');
    
    const plant = plantSelect.value;
    const variant = variantSelect.value;
    const weight = parseFloat(weightInput.value) || 0;
    const quantity = parseInt(quantityInput.value) || 1;
    
    // Get selected mutations
    const selectedMutations = Array.from(mutationsSelect.selectedOptions).map(option => option.value);
    
    if (!plant || !variant || weight <= 0) {
        resultDisplay.classList.add('hidden');
        return;
    }
    
    try {
        // Calculate plant value using existing API
        const response = await fetch(`${API_BASE}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                plant: plant,
                variant: variant,
                weight: weight,
                mutations: selectedMutations,
                amount: 1 // Calculate per plant first
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const perPlantValue = data.result_value;
            const totalValue = perPlantValue * quantity;
            
            // Update result display
            resultValue.textContent = formatLargeNumber(perPlantValue) + ' sheckles';
            resultDisplay.classList.remove('hidden');
            
            // Update batch plants array
            const plantIndex = batchPlants.findIndex(p => p.id === rowId);
            if (plantIndex !== -1) {
                batchPlants[plantIndex] = {
                    id: rowId,
                    plant: plant,
                    variant: variant,
                    weight: weight,
                    quantity: quantity,
                    mutations: selectedMutations,
                    result: perPlantValue,
                    total: totalValue
                };
            }
            
            // Update overall batch calculations
            updateBatchCalculations();
            
        } else {
            console.error('Failed to calculate plant value');
            resultDisplay.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error calculating plant value:', error);
        resultDisplay.classList.add('hidden');
    }
}

/**
 * Update overall batch calculations
 */
function updateBatchCalculations() {
    const totalValueElement = document.getElementById('batch-total-value');
    const totalPlantsElement = document.getElementById('batch-total-plants');
    const avgPerPlantElement = document.getElementById('batch-avg-per-plant');
    
    let totalValue = 0;
    let totalPlants = 0;
    let validPlants = 0;
    
    batchPlants.forEach(plant => {
        if (plant.result > 0) {
            totalValue += plant.total;
            totalPlants += plant.quantity;
            validPlants++;
        }
    });
    
    const avgPerPlant = validPlants > 0 ? totalValue / totalPlants : 0;
    
    // Update display
    if (totalValueElement) {
        totalValueElement.textContent = formatLargeNumber(totalValue) + ' sheckles';
    }
    
    if (totalPlantsElement) {
        totalPlantsElement.textContent = totalPlants;
    }
    
    if (avgPerPlantElement) {
        avgPerPlantElement.textContent = formatLargeNumber(avgPerPlant) + ' sheckles';
    }
}

/**
 * Initialize batch calculator
 */
function initializeBatchCalculator() {
    // Add plant row button
    const addPlantBtn = document.getElementById('add-plant-row');
    if (addPlantBtn) {
        addPlantBtn.addEventListener('click', addBatchPlantRow);
    }
    
    // Clear all button
    const clearAllBtn = document.getElementById('clear-batch-all');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearBatchAll);
    }
    
    // Share batch results button
    const shareBatchBtn = document.getElementById('share-batch-result');
    if (shareBatchBtn) {
        shareBatchBtn.addEventListener('click', shareBatchResults);
    }
}

/**
 * Clear all batch plants
 */
function clearBatchAll() {
    batchPlants = [];
    batchRowCounter = 0;
    
    const container = document.getElementById('batch-plant-rows');
    if (container) {
        container.innerHTML = '';
    }
    
    updateBatchCalculations();
}

/**
 * Share batch results
 */
async function shareBatchResults() {
    if (batchPlants.length === 0) {
        alert('No plants to share!');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/share-batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                plants: batchPlants
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const shareUrl = `${window.location.origin}/share/${data.share_id}`;
            
            // Copy to clipboard
            await navigator.clipboard.writeText(shareUrl);
            alert('Batch results link copied to clipboard!');
        } else {
            alert('Failed to share batch results');
        }
    } catch (error) {
        console.error('Error sharing batch results:', error);
        alert('Error sharing batch results');
    }
}

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing calculator...');
    
    // Check if key elements exist
    const keyElements = [
        'plant-grid', 'plant-search', 'plant-weight', 'plant-amount',
        'result-title', 'result-value', 'weight-range', 'total-multiplier',
        'mutation-search' // Add mutation search to key elements check
    ];
    
    keyElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            console.log(`✓ Found element: ${id}`);
        } else {
            console.warn(`✗ Missing element: ${id}`);
        }
    });
    
    initializeCalculatorForm();
    
    // Initialize tab system and batch calculator
    initializeTabSystem();
    initializeBatchCalculator();
});