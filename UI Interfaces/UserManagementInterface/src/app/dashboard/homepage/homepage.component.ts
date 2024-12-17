import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { VehicleDetailsComponent } from '../../vehicle-details/vehicle-details.component';
import { AuthService } from '../../shared/auth.service';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [VehicleDetailsComponent],
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {
   vehicles:any = [
      {
        id:"1",
        tagId:"001",
        email:"123@gmail.com"
      }
    ];
  
    constructor(private router: Router, private authService: AuthService) {}
    
    ngOnInit() {
      this.authService.fetchVehicles().subscribe(
        (respData)=>{
          console.log(respData);
          this.vehicles = respData
        }
      )
    }

    onRecharge() {
      this.router.navigate(['../dashboard/recharge'])
    }

    onChallan(vehicle:any) {
      this.router.navigate(['../dashboard/challan/',vehicle['id']])
    }
}
