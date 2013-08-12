function check() {
   var type = document.getElementById('typeProbleme').value;
   if (type == "Autre") {
      document.getElementById('typeautre').style.display = 'inline';
      document.getElementById('typeautre').className = 'required';
   } else if (type !== "Autre" ) {
      document.getElementById('typeautre').style.display = 'none';
      document.getElementById('typeautre').className = '';
   }
}
