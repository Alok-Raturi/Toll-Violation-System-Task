import { HeaderComponent } from '../header/header.component';
import { Component } from '@angular/core';
import { FooterComponent } from '../footer/footer.component';
import { VehicleDetailsComponent } from './vehicle-details/vehicle-details.component';
import { Router, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [HeaderComponent,FooterComponent,RouterOutlet],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  userName = "Madhur Gupta";
  loginReturn = {
    accessToken:"xyz",
    designation:"user",
    email:"abc@gmail.com",
    uid:"001"
  }
  vehicles = [
    {
      vid:"1",
      tag_id:"001",
      owner_email:"123@gmail.com"
    },
    {
      vid:"2",
      tag_id:"002",
      owner_email:"123@gmail.com"
    },
    {
      vid:"3",
      tag_id:"003",
      owner_email:"123@gmail.com"
    },
  ];

    constructor(private router: Router) {}

  onRecharge() {
    this.router.navigate(['../dashboard/recharge'])
  }
}
