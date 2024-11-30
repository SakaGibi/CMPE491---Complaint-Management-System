import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-main-menu',
  imports: [],
  templateUrl: './main-menu.component.html',
  styleUrl: './main-menu.component.css'
})
export class MainMenuComponent {

  constructor(private router: Router){}

  writeComplaintOrSuggestion(){
    // doldurulucak. 
  }

  toggleEmailInput() {
    const checkbox = document.getElementById('trackCheckBox') as HTMLInputElement | null;
    const emailInput = document.getElementById('emailInputContainer') as HTMLElement | null;

    if (checkbox && emailInput) { 
      if (checkbox.checked) {
        emailInput.style.display = 'block'; 
      } else {
        emailInput.style.display = 'none'; 
      }
    }
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToManagementPanelLogin() {
    this.router.navigate(['/managementPanelLogin']);
  }

}
