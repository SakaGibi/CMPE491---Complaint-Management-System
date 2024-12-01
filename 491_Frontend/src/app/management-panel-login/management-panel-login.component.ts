import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-management-panel-login',
  imports: [],
  templateUrl: './management-panel-login.component.html',
  styleUrl: './management-panel-login.component.css'
})
export class ManagementPanelLoginComponent {

  constructor(private router: Router){}

  goToManagementPanel() {
    this.router.navigate(['/managementPanel']);
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }

  

}
