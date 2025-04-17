import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-support',
  imports: [],
  templateUrl: './help-support.component.html',
  styleUrls: ['./help-support.component.css']
})
export class HelpSupportComponent { 

  constructor(private router: Router){}
  
  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }
}
