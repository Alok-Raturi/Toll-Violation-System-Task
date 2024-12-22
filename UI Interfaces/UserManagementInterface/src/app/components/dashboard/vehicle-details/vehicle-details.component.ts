import { Component, Input } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-vehicle-details',
  standalone: true,
  imports: [RouterLink],
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
