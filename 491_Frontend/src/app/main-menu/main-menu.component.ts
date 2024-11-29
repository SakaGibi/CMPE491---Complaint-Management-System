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

  goToHelpSupport() {
    this.router.navigate(['/help-support']);
  }

  goToManagementPanel() {
    this.router.navigate(['/management-panel']);
  }

}
