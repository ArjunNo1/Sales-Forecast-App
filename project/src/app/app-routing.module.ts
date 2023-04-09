import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DropComponent } from './drop/drop.component';
import { FormsComponent } from './forms/forms.component';
import { AppComponent } from './app.component';
const routes: Routes = [
  // { path :'', redirectTo: '/app', pathMatch: 'full'},
  { path: 'app', component: AppComponent},

  {path : 'datadrop',component:DropComponent},
  {path : 'forms',component :FormsComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
