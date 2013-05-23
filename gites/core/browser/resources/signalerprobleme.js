function check() {
   var type = document.getElementById('typeProbleme').value;
   if (type == "autre") {
      document.getElementById('typeautre').style.display = 'inline';
      document.getElementById('typeautre').className = 'required';
   } else if (type !== "autre" ) {
      document.getElementById('typeautre').style.display = 'none';
      document.getElementById('typeautre').className = '';
   }
}
