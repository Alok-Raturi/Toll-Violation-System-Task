import { Routes } from '@angular/router';
import { LoginPageComponent } from './components/login-page/login-page.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { FastTrackRechargeComponent } from './components/fast-track-recharge/fast-track-recharge.component';
import { VehicleDetailsComponent } from './components/dashboard/vehicle-details/vehicle-details.component';
import { HomepageComponent } from './components/dashboard/homepage/homepage.component';
import { ChallanPageComponent } from './components/dashboard/challan-page/challan-page.component';
import { isLoggedIn, isNotLoggedIn } from './guards/isLogin.guard';
import { TransactionHistoryComponent } from './components/transaction-history/transaction-history.component';
import { RechargeFastagComponent } from './components/recharge-fastag/recharge-fastag.component';

export const routes: Routes = [
    {
        path: 'login',
        component: LoginPageComponent,
        canActivate: [isNotLoggedIn],
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
                path: 'fastags',
                component: FastTrackRechargeComponent,
                canActivate: [isLoggedIn],
            },
            {
              path: 'recharge',
              component: RechargeFastagComponent,
              canActivate: [isLoggedIn],
          },
            {
              path: 'transaction-history/:id',
              component: TransactionHistoryComponent,
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
