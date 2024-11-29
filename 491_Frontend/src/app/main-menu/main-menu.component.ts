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

  //html'e eklenicek
  goToHelpSupport() {
    this.router.navigate(['/helpSupport']);
  }

  // html'e eklenicek
  goToManagementPanel() {
    this.router.navigate(['/managementPanel']);
  }

}
