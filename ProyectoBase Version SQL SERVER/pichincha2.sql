/*==============================================================*/
/* DBMS name:      Microsoft SQL Server 2008                    */
/* Created on:     30/07/2025 7:31:24                           */
/*==============================================================*/


/*==============================================================*/
/* Table: BOUCHER_CABECERA                                      */
/*==============================================================*/
create table BOUCHER_CABECERA (
   BAN_AID              varchar(14)          not null,
   BAN_NOMBRE           varchar(64)          not null,
   BAN_DIRECCION        varchar(64)          not null,
   BAN_RUC              varchar(13)          not null,
   BAN_MENSAJE          varchar(300)         not null,
   constraint PK_BOUCHER_CABECERA primary key nonclustered (BAN_AID)
)
go

/*==============================================================*/
/* Table: BOUCHER_CUERPO                                        */
/*==============================================================*/
create table BOUCHER_CUERPO (
   BOUC_ID              int                  not null,
   RETT_IMPRIMIR        varchar(2)           not null,
   RETT_MONTOMAX        int                  not null,
   TRAN_ID              int                  not null,
   RET_ID               int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   RET_FECHA            datetime             not null,
   RET_MONTO            int                  not null,
   RET_CAJERO           varchar(8)           not null,
   RET_NUMERO_TRAN      varchar(4)           not null,
   BAN_AID              varchar(14)          not null,
   BOUC_COSTO           decimal              not null,
   BOUC_TOTALDEBITADO   decimal              not null,
   constraint PK_BOUCHER_CUERPO primary key nonclustered (BOUC_ID, TRAN_ID, RET_ID)
)
go

/*==============================================================*/
/* Index: CABECERA_CUERPO_FK                                    */
/*==============================================================*/
create index CABECERA_CUERPO_FK on BOUCHER_CUERPO (
BAN_AID ASC
)
go

/*==============================================================*/
/* Index: HERENCIABOUCHER_FK                                    */
/*==============================================================*/
create index HERENCIABOUCHER_FK on BOUCHER_CUERPO (
TRAN_ID ASC,
RET_ID ASC
)
go

/*==============================================================*/
/* Table: CAJERO                                                */
/*==============================================================*/
create table CAJERO (
   CAJ_ID               int                  not null,
   CAJ_UBICACION        varchar(100)         not null,
   CAJ_ESTADO           varchar(20)          not null,
   CAJ_TIPO             varchar(30)          not null,
   CAJ_SUCURSAL         varchar(50)          not null,
   constraint PK_CAJERO primary key nonclustered (CAJ_ID)
)
go

/*==============================================================*/
/* Table: CLIENTE                                               */
/*==============================================================*/
create table CLIENTE (
   PER_ID               int                  not null,
   CLI_ID               int                  not null,
   PER_NOMBRES          varchar(300)         not null,
   PER_APELLIDOS        varchar(300)         not null,
   PER_FECHA_NACIMIENTO datetime             not null,
   PER_GENERO           varchar(64)          not null,
   PER_TELEFONO         varchar(10)          not null,
   PER_CORREO           varchar(64)          not null,
   PER_DIRECCION        varchar(124)         not null,
   PER_TIPO             varchar(64)          not null,
   CLI_FECHA_INGRESP    datetime             not null,
   CLI_ESTADO           varchar(64)          not null,
   constraint PK_CLIENTE primary key nonclustered (PER_ID, CLI_ID)
)
go

/*==============================================================*/
/* Index: HERENCIACLIENTE_FK                                    */
/*==============================================================*/
create index HERENCIACLIENTE_FK on CLIENTE (
PER_ID ASC
)
go

/*==============================================================*/
/* Table: CONDICIONES                                           */
/*==============================================================*/
create table CONDICIONES (
   COND_ID              int                  not null,
   COND_DESCRIPCION     varchar(200)         not null,
   COND_HORAS           int                  not null,
   COND_INTENTOS        int                  not null,
   COND_MONTO           int                  not null,
   COND_ESTADO          varchar(20)          not null,
   constraint PK_CONDICIONES primary key nonclustered (COND_ID)
)
go

/*==============================================================*/
/* Table: CONSULTA                                              */
/*==============================================================*/
create table CONSULTA (
   TRAN_ID              int                  not null,
   CONS_ID              int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   CONS_FECHA_HORA      datetime             not null,
   CONS_COMISION        decimal              not null,
   CONS_TIPO            varchar(100)         not null,
   CONS_RESULTADOS      text                 not null,
   constraint PK_CONSULTA primary key nonclustered (TRAN_ID, CONS_ID)
)
go

/*==============================================================*/
/* Index: HERENCIATRANSACCION_FK                                */
/*==============================================================*/
create index HERENCIATRANSACCION_FK on CONSULTA (
TRAN_ID ASC
)
go

/*==============================================================*/
/* Table: CUENTA                                                */
/*==============================================================*/
create table CUENTA (
   CUEN_ID              int                  not null,
   PER_ID               int                  not null,
   CLI_ID               int                  not null,
   CUEN_USUARIO         varchar(64)          not null,
   CUEN_PASSWORD        varchar(64)          not null,
   CUEN_TIPO            varchar(64)          not null,
   CUEN_NUMERO_CUENTA   varchar(10)          not null,
   CUEN_SALDO           decimal              not null,
   CUEN_ESTADO          varchar(64)          not null,
   constraint PK_CUENTA primary key nonclustered (CUEN_ID)
)
go

/*==============================================================*/
/* Index: CUENTA_CLIENTE_FK                                     */
/*==============================================================*/
create index CUENTA_CLIENTE_FK on CUENTA (
PER_ID ASC,
CLI_ID ASC
)
go

/*==============================================================*/
/* Table: CUENTA_AHORRO                                         */
/*==============================================================*/
create table CUENTA_AHORRO (
   CUEN_ID              int                  not null,
   PER_ID               int                  null,
   CLI_ID               int                  not null,
   CUEN_USUARIO         varchar(64)          not null,
   CUEN_PASSWORD        varchar(64)          not null,
   CUEN_TIPO            varchar(64)          not null,
   CUEN_NUMERO_CUENTA   varchar(10)          not null,
   CUEN_SALDO           decimal              not null,
   CUEN_ESTADO          varchar(64)          not null,
   CA_INTERES           decimal              not null,
   CA_LIMITE_RETIROS    int                  not null,
   CA_MIN_SALDO_REMUNERADO decimal              not null,
   constraint PK_CUENTA_AHORRO primary key nonclustered (CUEN_ID)
)
go

/*==============================================================*/
/* Table: CUENTA_CORRIENTE                                      */
/*==============================================================*/
create table CUENTA_CORRIENTE (
   CUEN_ID              int                  not null,
   PER_ID               int                  null,
   CLI_ID               int                  not null,
   CUEN_USUARIO         varchar(64)          not null,
   CUEN_PASSWORD        varchar(64)          not null,
   CUEN_TIPO            varchar(64)          not null,
   CUEN_NUMERO_CUENTA   varchar(10)          not null,
   CUEN_SALDO           decimal              not null,
   CUEN_ESTADO          varchar(64)          not null,
   CC_LIMITE_DESCUBIERTO decimal              not null,
   CC_COMISION_MANTENIMIENTO decimal              not null,
   CC_NUM_CHEQUES       int                  not null,
   constraint PK_CUENTA_CORRIENTE primary key nonclustered (CUEN_ID)
)
go

/*==============================================================*/
/* Table: DEPOSITOS                                             */
/*==============================================================*/
create table DEPOSITOS (
   TRAN_ID              int                  not null,
   DEP_ID               int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   DEP_FECHA            datetime             not null,
   DEP_MONTO            decimal              not null,
   DEP_CUENTA_DEST      varchar(20)          not null,
   DEP_CANAL            varchar(20)          not null,
   DEP_REFERENCIA       varchar(30)          not null,
   DEP_ESTADO           varchar(20)          not null,
   constraint PK_DEPOSITOS primary key nonclustered (TRAN_ID, DEP_ID)
)
go

/*==============================================================*/
/* Index: HERENCIATRANSACCION3_FK                               */
/*==============================================================*/
create index HERENCIATRANSACCION3_FK on DEPOSITOS (
TRAN_ID ASC
)
go

/*==============================================================*/
/* Table: PAGO_SERVICIOS                                        */
/*==============================================================*/
create table PAGO_SERVICIOS (
   TRAN_ID              int                  not null,
   PS_ID                int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   PS_TIPO_SERVICIO     varchar(100)         not null,
   PS_PROVEEDOR         varchar(100)         not null,
   PS_REFERENCIA        varchar(100)         not null,
   PS_MONTO             decimal              not null,
   PS_FECHA_HORA        datetime             not null,
   PS_COMISION          decimal              not null,
   PS_RESULTADO_CODIGO  varchar(10)          not null,
   PS_ESTADO            varchar(20)          not null,
   PS_COMPROBANTE       text                 not null,
   constraint PK_PAGO_SERVICIOS primary key nonclustered (TRAN_ID, PS_ID)
)
go

/*==============================================================*/
/* Index: HERENCIATRANSACCION2_FK                               */
/*==============================================================*/
create index HERENCIATRANSACCION2_FK on PAGO_SERVICIOS (
TRAN_ID ASC
)
go

/*==============================================================*/
/* Table: PERSONA                                               */
/*==============================================================*/
create table PERSONA (
   PER_ID               int                  not null,
   PER_NOMBRES          varchar(300)         not null,
   PER_APELLIDOS        varchar(300)         not null,
   PER_FECHA_NACIMIENTO datetime             not null,
   PER_GENERO           varchar(64)          not null,
   PER_TELEFONO         varchar(10)          not null,
   PER_CORREO           varchar(64)          not null,
   PER_DIRECCION        varchar(124)         not null,
   PER_TIPO             varchar(64)          not null,
   constraint PK_PERSONA primary key nonclustered (PER_ID)
)
go

/*==============================================================*/
/* Table: PERSONA_JURIDICA                                      */
/*==============================================================*/
create table PERSONA_JURIDICA (
   PER_ID               int                  not null,
   PER_NOMBRES          varchar(300)         not null,
   PER_APELLIDOS        varchar(300)         not null,
   PER_FECHA_NACIMIENTO datetime             not null,
   PER_GENERO           varchar(64)          not null,
   PER_TELEFONO         varchar(10)          not null,
   PER_CORREO           varchar(64)          not null,
   PER_DIRECCION        varchar(124)         not null,
   PER_TIPO             varchar(64)          not null,
   PJ_RUC               varchar(13)          not null,
   PJ_REPRESENTANTE     varchar(100)         not null,
   PJ_TIPO_ENTIDAD      varchar(50)          not null,
   PJ_FECHA_CONSTITUCION datetime             not null,
   PJ_ACTIVIDAD         varchar(200)         not null,
   constraint PK_PERSONA_JURIDICA primary key nonclustered (PER_ID)
)
go

/*==============================================================*/
/* Table: PERSONA_NATURAL                                       */
/*==============================================================*/
create table PERSONA_NATURAL (
   PER_ID               int                  not null,
   PER_NOMBRES          varchar(300)         not null,
   PER_APELLIDOS        varchar(300)         not null,
   PER_FECHA_NACIMIENTO datetime             not null,
   PER_GENERO           varchar(64)          not null,
   PER_TELEFONO         varchar(10)          not null,
   PER_CORREO           varchar(64)          not null,
   PER_DIRECCION        varchar(124)         not null,
   PER_TIPO             varchar(64)          not null,
   PN_IDENTIFICACION    varchar(13)          not null,
   PN_ESTADO_CIVIL      varchar(20)          not null,
   PN_PROFESION         varchar(100)         not null,
   constraint PK_PERSONA_NATURAL primary key nonclustered (PER_ID)
)
go

/*==============================================================*/
/* Table: RETIRO                                                */
/*==============================================================*/
create table RETIRO (
   TRAN_ID              int                  not null,
   RET_ID               int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   RET_FECHA            datetime             not null,
   RET_MONTO            int                  not null,
   RET_CAJERO           varchar(8)           not null,
   RET_NUMERO_TRAN      varchar(4)           not null,
   constraint PK_RETIRO primary key nonclustered (TRAN_ID, RET_ID)
)
go

/*==============================================================*/
/* Index: HERENCIATRANSACCION5_FK                               */
/*==============================================================*/
create index HERENCIATRANSACCION5_FK on RETIRO (
TRAN_ID ASC
)
go

/*==============================================================*/
/* Table: RETIRO_CONTARJETA                                     */
/*==============================================================*/
create table RETIRO_CONTARJETA (
   TRAN_ID              int                  not null,
   RET_ID               int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   RET_FECHA            datetime             not null,
   RET_MONTO            int                  not null,
   RET_CAJERO           varchar(8)           not null,
   RET_NUMERO_TRAN      varchar(4)           not null,
   RETT_IMPRIMIR        varchar(2)           not null,
   RETT_MONTOMAX        int                  not null,
   constraint PK_RETIRO_CONTARJETA primary key nonclustered (TRAN_ID, RET_ID)
)
go

/*==============================================================*/
/* Table: RETIRO_SINTARJETA                                     */
/*==============================================================*/
create table RETIRO_SINTARJETA (
   TRAN_ID              int                  not null,
   RET_ID               int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   RET_FECHA            datetime             not null,
   RET_MONTO            int                  not null,
   RET_CAJERO           varchar(8)           not null,
   RET_NUMERO_TRAN      varchar(4)           not null,
   COND_ID              int                  not null,
   RETS_CODIGO          varchar(8)           not null,
   RETS_TELEFONO_ASOCIADO varchar(10)          not null,
   RETS_ESTADO_CODIGO   varchar(64)          not null,
   constraint PK_RETIRO_SINTARJETA primary key nonclustered (TRAN_ID, RET_ID)
)
go

/*==============================================================*/
/* Index: CONDICIONES_TARJETA_FK                                */
/*==============================================================*/
create index CONDICIONES_TARJETA_FK on RETIRO_SINTARJETA (
COND_ID ASC
)
go

/*==============================================================*/
/* Table: TARJETA                                               */
/*==============================================================*/
create table TARJETA (
   TAR_ID               int                  not null,
   CUEN_ID              int                  not null,
   TAR_NUMERO_TARJETA   varchar(16)          not null,
   TAR_FECHA_EMISION    datetime             not null,
   TAR_FECHA_EXPIRACION datetime             not null,
   TAR_ESTADO_TARJETA   varchar(64)          not null,
   TAR_CVV              varchar(3)           not null,
   TAR_TIPO             varchar(64)          not null,
   TAR_PIN              varchar(4)           not null,
   constraint PK_TARJETA primary key nonclustered (TAR_ID)
)
go

/*==============================================================*/
/* Index: CUENTA_TARJETA_FK                                     */
/*==============================================================*/
create index CUENTA_TARJETA_FK on TARJETA (
CUEN_ID ASC
)
go

/*==============================================================*/
/* Table: TARJETA_CREDITO                                       */
/*==============================================================*/
create table TARJETA_CREDITO (
   TAR_ID               int                  not null,
   CUEN_ID              int                  not null,
   TAR_NUMERO_TARJETA   varchar(16)          not null,
   TAR_FECHA_EMISION    datetime             not null,
   TAR_FECHA_EXPIRACION datetime             not null,
   TAR_ESTADO_TARJETA   varchar(64)          not null,
   TAR_CVV              varchar(3)           not null,
   TAR_TIPO             varchar(64)          not null,
   TAR_PIN              varchar(4)           not null,
   TC_LIMITE_CREDITO    decimal              not null,
   TC_TASA_INTERES      decimal              not null,
   TC_CARGO_ANUAL       decimal              not null,
   TC_FECHA_CORTE       datetime             not null,
   TC_FECHA_VENCIMIENTO datetime             not null,
   TC_MOROSIDAD         bit                  not null,
   constraint PK_TARJETA_CREDITO primary key nonclustered (TAR_ID)
)
go

/*==============================================================*/
/* Table: TARJETA_DEBITO                                        */
/*==============================================================*/
create table TARJETA_DEBITO (
   TAR_ID               int                  not null,
   CUEN_ID              int                  not null,
   TAR_NUMERO_TARJETA   varchar(16)          not null,
   TAR_FECHA_EMISION    datetime             not null,
   TAR_FECHA_EXPIRACION datetime             not null,
   TAR_ESTADO_TARJETA   varchar(64)          not null,
   TAR_CVV              varchar(3)           not null,
   TAR_TIPO             varchar(64)          not null,
   TAR_PIN              varchar(4)           not null,
   TD_LIMITE_RETIRO_DIARIO decimal              not null,
   TD_COMISION_SOBREGIRO decimal              not null,
   constraint PK_TARJETA_DEBITO primary key nonclustered (TAR_ID)
)
go

/*==============================================================*/
/* Table: TRANSACCION                                           */
/*==============================================================*/
create table TRANSACCION (
   TRAN_ID              int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   constraint PK_TRANSACCION primary key nonclustered (TRAN_ID)
)
go

/*==============================================================*/
/* Index: CUENTA_TRANSACCION_FK                                 */
/*==============================================================*/
create index CUENTA_TRANSACCION_FK on TRANSACCION (
CUEN_ID ASC
)
go

/*==============================================================*/
/* Index: TRANSACCION_CAJERO_FK                                 */
/*==============================================================*/
create index TRANSACCION_CAJERO_FK on TRANSACCION (
CAJ_ID ASC
)
go

/*==============================================================*/
/* Table: TRANSFERENCIA                                         */
/*==============================================================*/
create table TRANSFERENCIA (
   TRAN_ID              int                  not null,
   TRANS_ID             int                  not null,
   CUEN_ID              int                  not null,
   CAJ_ID               int                  not null,
   TRANS_FECHA          datetime             not null,
   TRANS_MONTO          decimal              not null,
   TRANS_ORIGEN         varchar(20)          not null,
   TRANS_DESTINO        varchar(20)          not null,
   TRANS_CANAL          varchar(20)          not null,
   TRANS_ESTADO         varchar(20)          not null,
   constraint PK_TRANSFERENCIA primary key nonclustered (TRAN_ID, TRANS_ID)
)
go

/*==============================================================*/
/* Index: HERENCIATRANSACCION4_FK                               */
/*==============================================================*/
create index HERENCIATRANSACCION4_FK on TRANSFERENCIA (
TRAN_ID ASC
)
go

alter table BOUCHER_CUERPO
   add constraint FK_BOUCHER__CABECERA__BOUCHER_ foreign key (BAN_AID)
      references BOUCHER_CABECERA (BAN_AID)
go

alter table BOUCHER_CUERPO
   add constraint FK_BOUCHER__HERENCIAB_RETIRO_C foreign key (TRAN_ID, RET_ID)
      references RETIRO_CONTARJETA (TRAN_ID, RET_ID)
go

alter table CLIENTE
   add constraint FK_CLIENTE_HERENCIAC_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
go

alter table CONSULTA
   add constraint FK_CONSULTA_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
go

alter table CUENTA
   add constraint FK_CUENTA_CUENTA_CL_CLIENTE foreign key (PER_ID, CLI_ID)
      references CLIENTE (PER_ID, CLI_ID)
go

alter table CUENTA_AHORRO
   add constraint FK_CUENTA_A_HERENCIAC_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
go

alter table CUENTA_CORRIENTE
   add constraint FK_CUENTA_C_HERENCIAC_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
go

alter table DEPOSITOS
   add constraint FK_DEPOSITO_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
go

alter table PAGO_SERVICIOS
   add constraint FK_PAGO_SER_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
go

alter table PERSONA_JURIDICA
   add constraint FK_PERSONA__HERENCIA4_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
go

alter table PERSONA_NATURAL
   add constraint FK_PERSONA__HERENCIA3_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
go

alter table RETIRO
   add constraint FK_RETIRO_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
go

alter table RETIRO_CONTARJETA
   add constraint FK_RETIRO_C_INHERITAN_RETIRO foreign key (TRAN_ID, RET_ID)
      references RETIRO (TRAN_ID, RET_ID)
go

alter table RETIRO_SINTARJETA
   add constraint FK_RETIRO_S_CONDICION_CONDICIO foreign key (COND_ID)
      references CONDICIONES (COND_ID)
go

alter table RETIRO_SINTARJETA
   add constraint FK_RETIRO_S_INHERITAN_RETIRO foreign key (TRAN_ID, RET_ID)
      references RETIRO (TRAN_ID, RET_ID)
go

alter table TARJETA
   add constraint FK_TARJETA_CUENTA_TA_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
go

alter table TARJETA_CREDITO
   add constraint FK_TARJETA__HERENCIA_TARJETA foreign key (TAR_ID)
      references TARJETA (TAR_ID)
go

alter table TARJETA_DEBITO
   add constraint FK_TARJETA__HERENCIA2_TARJETA foreign key (TAR_ID)
      references TARJETA (TAR_ID)
go

alter table TRANSACCION
   add constraint FK_TRANSACC_CUENTA_TR_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
go

alter table TRANSACCION
   add constraint FK_TRANSACC_TRANSACCI_CAJERO foreign key (CAJ_ID)
      references CAJERO (CAJ_ID)
go

alter table TRANSFERENCIA
   add constraint FK_TRANSFER_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
go

