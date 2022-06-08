# Overview

***
*This site is under construction. Please treat it as ALPHA version. Any comments & reviews are welcomed!*
***

This repository contains a set of [ovirt-engine setup plugins](https://www.ovirt.org/develop/developer-guide/engine/engine-setup.html) that allow to install and setup [Keycloak overlay](https://www.keycloak.org/docs/latest/server_installation/#installing-the-software) package as internal Single-Sign-On (SSO) provider for oVirt Engine, thus deprecating oVirt Engine's [AAA](https://www.ovirt.org/documentation/administration_guide/index.html#chap-Users_and_Roles). In addition, [oVirt Provider OVN](https://github.com/oVirt/ovirt-provider-ovn)  and [Grafana / Monitoring Portal](https://www.ovirt.org/documentation/administration_guide/index.html#using-data-warehouse-and-grafana-to-monitor-ovirt) are being reconfigured to use Keycloak SSO as well.

# Usage scenarios and current limitations

## Fresh (default) installation of oVirt 4.5.1 and above.

For fresh installation internally bundled Keycloak becomes the default SSO provider. However, if system administrator decides otherwise it is possible to fall back to legacy AAA configuration by rejecting Keycloak during `engine-setup` run.

### Use legacy AAA for fresh installation
In order to use legacy AAA authentication please provide 'No' for the following `engine-setup` questions
```
          * Please note * : Keycloak is now deprecating AAA/JDBC authentication module.
          It is highly recommended to install Keycloak based authentication.
          Configure Keycloak on this host (Yes, No) [Yes]:
          provided answer: no

          Are you really sure not to install internal Keycloak based authentication?
          AAA modules are being deprecated
          Configure Keycloak on this host (Yes, No) [Yes]:
          provided answer: no
```

Also `hosted-engine --deploy` asks:
```
         Configure Keycloak integration on the engine (Yes, No) [Yes]:
```

## Reconfiguration from oVirt 4.5.1 and above

If the system administrator originally disabled the internal Keycloak for oVirt >= 4.5.1, and later decides to make a switch, it is possible to do so. The trade-off is that any existing AAA configuration will have to be migrated to Keycloak manually.
In order to activate the internal Keycloak, please see the [activation procedure](#Internal-Keycloak-activation-procedure).


## Upgrade from existing oVirt Engine installations (oVirt <= 4.5.0)

When upgrading the existing oVirt installation to version >= 4.5.1, due to backward compatibility, oVirt AAA configuration is the preferred solution. There will be no Keycloak related questions during engine-setup execution. System administrators can decide, whether to migrate manually as documented [here](https://blogs.ovirt.org/2019/01/federate-ovirt-engine-authentication-to-openid-connect-infrastructure/), or keep using their existing setup. At current time there are no automatic migration from AAA JDBC or AAA LDAP to internally bundled Keycloak.
In order to activate the internal Keycloak please see the [activation procedure](#Internal-Keycloak-activation-procedure).

## Development environment
Keycloak is not supposed to be installed and configured on [the development environment](https://www.ovirt.org/develop/developer-guide/engine/engine-development-environment.html).

## Internal Keycloak activation procedure

In case system administrator decides to enable internally bundled Keycloak SSO there are the following steps needed:
1. Backup existing setup (full backup & restore exercise is highly recommended)
2. Enable internally bundled Keycloak. Please note that any existing user base setup needs to be migrated manually. Please see Keycloak documentation how to setup various user backends (todo: links)
```
engine-setup --otopi-environment="OVESETUP_CONFIG/keycloakEnable=bool:True"
```
3. To test the setup please login to Administration Portal using the admin username: `admin@ovirt` and provided password. For REST API access the full username with profile must be provided: `admin@ovirt@internalsso`. In order to login to Keycloak Administration Console please use `admin` and provided password (from the above).
   Additionally, the `engine-setup` output should contain a confirmation that Keycloak has been configured.
```
          --== SUMMARY ==--                                                                                                          
                                                                                                                                     
[ INFO  ] Starting service: grafana-server                                                                                          
[ INFO  ] Starting dwh service                                                                                                      
[ INFO  ] Starting Grafana service                                                                                                  
[ INFO  ] Restarting ovirt-vmconsole proxy service                                                                                  
          Please use the user 'admin' and password specified in order to login to Keycloak admin console           
          Please use the user 'admin@ovirt' and password specified in order to login using Keycloak SSO                              
          Web access is enabled at:                                                                                                 
              http://dev2.dom:80/ovirt-engine                                                                                       
              https://dev2.dom:443/ovirt-engine                                                                                     
          Internal CA fingerprint: SHA256: 4E:A7:F0:71:92:A1:7B:C0:37:2C:4D:DF:86:2D:70:94:E3:7B:DC:FA:0F:44:00:F3:81:E4:35:83:3C:E0:
DF:8F                                                                                                                               
          SSH fingerprint: SHA256:3gsIvHFk+irCRfmtSXbDSOdXYjgGVgoxTMUteBJ/nv0                                                       
[ INFO  ] Starting engine service                                
[WARNING] Less than 16384MB of memory is available                                                                                  
          Web access for grafana is enabled at:                                                                                     
              https://dev2.dom/ovirt-engine-grafana/                                                                                
          Please run the following command on the engine machine dev2.dom, for SSO to work:                                         
          systemctl restart ovirt-engine                                                                                            
          Keycloak database resources:                                                     
              Database name:      ovirt_engine_keycloak_20220519111841                 
              Database user name: ovirt_engine_keycloak_20220519111841 
                                                           
          --== END OF SUMMARY ==--                                              
                                                                                       
[ INFO  ] Restarting httpd                                                  
[ INFO  ] Start with setting up Keycloak for Ovirt Engine                                                
[ INFO  ] Done with setting up Keycloak for Ovirt Engine                                        
[ INFO  ] Stage: Clean up                                                                                                            
          Log file is located at /var/log/ovirt-engine/setup/ovirt-engine-setup-20220519111823-q89zni.log
[ INFO  ] Generating answer file '/var/lib/ovirt-engine/setup/answers/20220519112026-setup.conf'                                     
[ INFO  ] Stage: Pre-termination                                                                                                     
[ INFO  ] Stage: Termination                                                           
[ INFO  ] Execution of setup completed successfully                                                                                  
```

# Current limitations

## Fallback
There is no automated fallback script from the internal Keycloak to legacy AAA modules. However, this can be done manually if needed but is not recommended.

## Remote hosts
In case the Grafana (for Monitoring Portal) is configured to run on a separate host (different from where oVirt Engine is deployed) the SSO  will not work out-of-the-box. Relevant configuration in `/etc/grafana/grafana.ini` must be updated. However, it would be still possible to login using grafana bootstrap admin user.

## No automated migration for either AAA JDBC or AAA LDAP
Currently, we do not have any automation to help to migrate existing AAA environments. Feel free to file bugzilla requests or GitHub issues if needed.



 


