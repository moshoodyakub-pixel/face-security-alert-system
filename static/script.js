document.getElementById('add-appliance').addEventListener('click', function() {
    var applianceDiv = document.createElement('div');
    applianceDiv.classList.add('appliance');
    applianceDiv.innerHTML = `
        <input type="text" name="appliance_name[]" placeholder="Appliance Name" required>
        <input type="number" name="quantity[]" placeholder="Quantity" required>
        <input type="number" name="wattage[]" placeholder="Wattage" required>
        <input type="number" name="hours[]" placeholder="Daily Usage (hours)" required>
    `;
    document.getElementById('appliances').appendChild(applianceDiv);
});
