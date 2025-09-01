// Calculation logic and result display
export async function calculatePlantValue(currentPlant, currentVariant, selectedMutations, API_BASE) {
    const weightInput = document.getElementById('plant-weight');
    const amountInput = document.getElementById('plant-amount');
    if (!weightInput || !amountInput) return;
    const plantName = currentPlant;
    const weight = parseFloat(weightInput.value);
    const amount = parseInt(amountInput.value);
    console.log('Calculating for:', plantName, weight, amount, selectedMutations);
    if (!plantName || !weight || weight <= 0 || !amount || amount <= 0) {
        console.log('Invalid inputs, hiding results');
        if (window.hideResults) window.hideResults();
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
        if (!response.ok) throw new Error('Calculation failed');
        const result = await response.json();
        if (window.displayResults) window.displayResults(result);
    } catch (error) {
        console.error('Calculation error:', error);
        if (window.hideResults) window.hideResults();
    }
}

export function displayResults(result) {
}

// Exported for UI auto calculation
export function updateCalculationIfReady(currentPlant, currentVariant, selectedMutations, API_BASE) {
    if (currentPlant) {
        calculatePlantValue(currentPlant, currentVariant, selectedMutations, API_BASE);
    }
}
