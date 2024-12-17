import { Routes } from '@angular/router';
import { LoginPageComponent } from './login-page/login-page.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { FastTrackRechargeComponent } from './fast-track-recharge/fast-track-recharge.component';
import { VehicleDetailsComponent } from './vehicle-details/vehicle-details.component';
import { HomepageComponent } from './dashboard/homepage/homepage.component';
import { ChallanPageComponent } from './dashboard/challan-page/challan-page.component';
import { isLoggedIn } from './guards/isLogin.guard';

export const routes: Routes = [
    {
        path: 'login',
        component: LoginPageComponent
    },
    {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [isLoggedIn],
        children:[
            {
                path:'',
                redirectTo: 'home',
                pathMatch: 'full'
                
            },
            {
                path: 'home',
                component: HomepageComponent,
                canActivate: [isLoggedIn],
            },
            {
                path: 'recharge',
                component: FastTrackRechargeComponent,
                canActivate: [isLoggedIn],
            },
            {
                path: 'challan/:id',
                component: ChallanPageComponent,
                canActivate: [isLoggedIn],
            }
        ]

    },
    {
        path: '**',
        redirectTo: 'login'
    }
];

/*
        children: [
            {
                path: 'home',
                component: VehicleDetailsComponent,
            },
            {
                path: 'recharge',
                component: FastTrackRechargeComponent,
            }
        ]
*/