import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-vehicle-details',
  standalone: true,
  imports: [],
  templateUrl: './vehicle-details.component.html',
  styleUrl: './vehicle-details.component.css'
})
export class VehicleDetailsComponent {
  @Input('detail') vehicleDetail!: any;

  constructor(private router: Router){}

  onChallan(vehicle:any) {
    this.router.navigate(['/dashboard/challan/',vehicle['id']])
  }
}
