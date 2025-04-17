import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: 'app-management-panel-login',
  imports: [FormsModule],
  templateUrl: './management-panel-login.component.html',
  styleUrl: './management-panel-login.component.css'
})
export class ManagementPanelLoginComponent {

  username: string = '';
  password: string = '';
  isAdmin: boolean = false;

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

  changeIsAdmin(){
    this.isAdmin = !this.isAdmin
  }
  
  onLoginSubmit() {
    if (this.isAdmin) {
      this.router.navigate(['/adminPanel']);
    } else {
      this.router.navigate(['/managementPanel']);
    }
  }

}
