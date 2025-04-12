function enableEditing() {
    let inputs = document.querySelectorAll("#profile-form input");
    inputs.forEach(input => input.removeAttribute("disabled"));
    
    document.getElementById("edit-profile-btn").style.display = "none";
    document.getElementById("save-btn").style.display = "inline-block";
}