function check() {
   var type = document.getElementById('typeProbleme').value;
   if (type == "autre") {
      document.getElementById('typeautre').style.display = 'inline';
   } else if (type !== "autre" ) {
      document.getElementById('typeautre').style.display = 'none';
   }
}
