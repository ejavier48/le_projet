import { Component, OnInit } from '@angular/core';
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';
//para mostrar el loading
import { LoadingController } from '@ionic/angular';
//para recibir parametros
import { ActivatedRoute } from "@angular/router";
//mostrar alerta
import { AlertController } from '@ionic/angular';
//para poder moverme entre pantallas
import { Router } from "@angular/router";
//para usar Modals
import { ModalController } from '@ionic/angular';
//pagina que es mi Modal
import { ModalInterfacesPage } from "../modal-interfaces/modal-interfaces.page"


@Component({
  selector: 'app-ver-agente',
  templateUrl: './ver-agente.page.html',
  styleUrls: ['./ver-agente.page.scss'],
})
export class VerAgentePage implements OnInit {
  agente=[];
  ipAdd:string;
  numIterfaces:number;
  urlVolver:string;
  puerto:string;
  indice:string;
  imagenip : string = '';
  imagenicmp : string = '';
  imagentcp : string = '';
  imagenudp : string = '';
  imagenesip :string[] = ['', 'https://i.ytimg.com/vi/kV4vHpqrj6E/hqdefault.jpg'];
  imagenesicmp :string[] = ['', 'https://i.ytimg.com/vi/kV4vHpqrj6E/hqdefault.jpg'];
  imagenestcp :string[] = ['', 'https://i.ytimg.com/vi/kV4vHpqrj6E/hqdefault.jpg'];
  imagenesudp :string[] = ['', 'https://i.ytimg.com/vi/kV4vHpqrj6E/hqdefault.jpg'];
  index : number = 0;
  tiempo;
  constructor(private FlaskService: MensajeroFlaskService,
     private loadcont: LoadingController,
     private activatedRoute: ActivatedRoute,
     private alertController: AlertController,
     private router:Router,
     public modalController: ModalController) {
    //this.agente = this.FlaskService.agenteConsultado;
    //console.log(this.agente);
    this.indice = this.activatedRoute.snapshot.paramMap.get('indice');
    this.ipAdd=this.FlaskService.ipAdd;
    this.puerto=this.FlaskService.puerto;
  }

  volver(){
      this.router.navigate(['/menu',this.ipAdd, this.puerto,'menu','menu','consulta',this.ipAdd, this.puerto]);

  }

  async abrirModal(index:number){
    const modal = await this.modalController.create({
       component: ModalInterfacesPage,
       componentProps: { value: index, name:this.agente[0]._hostName, interface:this.agente[0]._interfaces[index].name }
     });
     return await modal.present();
  }

  ionViewWillEnter(){
      this.getData()
      let intervalHandle = setInterval(()=> {
        this.imagenip = this.imagenesip[this.index];
        this.imagentcp = this.imagenestcp[this.index];
        this.imagenudp = this.imagenesudp[this.index];
        this.imagenicmp = this.imagenesicmp[this.index];
        this.index++;

        if(this.index == this.imagenesip.length)
        {
          this.index=0;

        }

        this.tiempo=this.getFormattedDate();

      },2000);

  }
  getFormattedDate() {
    var date = new Date();
    var str = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " +  date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

    return str;
  }

  inicializaImagenes(){
    this.imagenip="http://192.168.0.25:8080/images/"+this.agente[0]._hostName+"/ip";
    this.imagenesip[0]=this.imagenip;
    this.imagenudp="http://192.168.0.25:8080/images/"+this.agente[0]._hostName+"/udp";
    this.imagenesudp[0]=this.imagenudp;
    this.imagentcp="http://192.168.0.25:8080/images/"+this.agente[0]._hostName+"/tcp";
    this.imagenestcp[0]=this.imagentcp;
    this.imagenicmp="http://192.168.0.25:8080/images/"+this.agente[0]._hostName+"/icmp";
    this.imagenesicmp[0]=this.imagenicmp;
  }

  async getData(){
    let data;
    const loading = await this.loadcont.create({
      message: 'Preguntando a los duendes de SNMP'
    });
    await loading.present();

    this.FlaskService.getData(this.FlaskService.ipAdd,this.FlaskService.puerto)
      .subscribe(res => {
        this.agente.push(res.devices[this.indice]);
          //console.log("data obtenida "+JSON.stringify(data));
        console.log(JSON.stringify(this.agente))
        this.FlaskService.generateImages(this.ipAdd);

        this.inicializaImagenes()



        loading.dismiss();
      },err => {
        console.log("error:"+JSON.stringify(err));
        //this.router.navigate(['/']);
          loading.dismiss();
          this.presentAlert(JSON.stringify(err));

      });
  }

  async presentAlert(mensaje:string) {

  const alert = await this.alertController.create({
    header: 'Error de conexion',
    subHeader: 'No se ha podido establer la conexion con el servidor',
    message: mensaje,
    buttons: ['OK']
  });
  await alert.present();
}


  ngOnInit() {}

}
