import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-challan-page',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './challan-page.component.html',
  styleUrl: './challan-page.component.css'
})
export class ChallanPageComponent {
  challanReturn:any = [
    {
      id:"1",
      vehicleId:"01",
      description:"No Helmet",
      location:"Jaipur",
      timestamp:"19:08:2024",
      amount: "100",
      status:"Settled",
      settlementDate:"27:08:2024",
    },
    {
      id:"2",
      vehicleId:"01",
      description:"Crash",
      location:"Noida",
      timestamp:"07:10:2024",
      amount: "1000",
      status:"Unsettled",
      dueDate:"7:11:2024"
    },
    {
      id:"3",
      vehicleId:"02",
      description:"Mass Murder",
      location:"Delhi",
      timestamp:"25:12:2024",
      amount: "100000",
      status:"Unsettled",
      dueDate:"11:01:2025",
    },
  ]
  vehicleId:string= ""

  constructor(private router: Router,private activatedRoute: ActivatedRoute, private authService: AuthService) {}

  ngOnInit() {
     this.activatedRoute.params.subscribe(
      (params)=>{
        this.authService.fetchChallan(params['id']).subscribe(
          (respData)=>{
            console.log(respData);
            this.vehicleId=params['id']
            this.challanReturn=respData
          }
        );
      }
     );
  }

  getDueDate(due_time:number){
    return new Date(due_time*1000)
  }

  payAChallan(id:string){
    return this.authService.paySingleChallan(id).subscribe()
  }

  payAllChallan(vid:string){
    return this.authService.payAllChallan(vid).subscribe()
  }
}
