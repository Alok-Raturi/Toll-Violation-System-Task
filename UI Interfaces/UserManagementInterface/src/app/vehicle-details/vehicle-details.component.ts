import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-vehicle-details',
  standalone: true,
  imports: [],
  templateUrl: './vehicle-details.component.html',
  styleUrl: './vehicle-details.component.css'
})
export class VehicleDetailsComponent {
  @Input('detail') vehicleDetail!: any;

}
