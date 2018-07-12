package tr.org.liderahenk.ldaplogin.dialogs;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import tr.org.liderahenk.ldaplogin.constants.LDAPLoginConstants;
import tr.org.liderahenk.liderconsole.core.current.UserSettings;
import tr.org.liderahenk.liderconsole.core.dialogs.DefaultTaskDialog;
import tr.org.liderahenk.liderconsole.core.exceptions.ValidationException;
import tr.org.liderahenk.liderconsole.core.ldap.listeners.LdapConnectionListener;
import tr.org.liderahenk.liderconsole.core.ldap.utils.LdapUtils;

/**
 * Task execution dialog for ldap-login plugin.
 * 
 */
public class LDAPLoginTaskDialog extends DefaultTaskDialog {
	
	private static final Logger logger = LoggerFactory.getLogger(LDAPLoginTaskDialog.class);
	private Label lblLDAPServerIP;
	private Label lblLDAPDN;
	private Label lblLDAPVersion;
	private Label lblLDAPAdminDN;
	private Label lblLDAPAdminPassword;
	
	private Text textLDAPServerIP;
	private Text textLDAPDN;
	private Text textLDAPVersion;
	private Text textLDAPAdminDN;
	private Text textLDAPAdminPassword;
	
	private Shell shell;
	
	// TODO do not forget to change this constructor if SingleSelectionHandler is used!
	public LDAPLoginTaskDialog(Shell parentShell, Set<String> dnSet) {
		super(parentShell, dnSet);
		shell = parentShell;
	}

	@Override
	public String createTitle() {
		// TODO dialog title
		return "LDAP Login";
	}

	@Override
	public Control createTaskDialogArea(Composite parent) {
		Composite composite = new Composite(parent, GridData.FILL);
		composite.setLayout(new GridLayout(2, false));

		GridData data= new GridData(SWT.FILL, SWT.FILL, true, true,1,1);
        data.widthHint=600;
        data.heightHint=500;
		
		composite.setLayoutData(data);
        
        //LDAP Server IP
		lblLDAPServerIP = new Label(composite, SWT.NONE);
		lblLDAPServerIP.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1));
		lblLDAPServerIP.setText("LDAP Sunucu Adresi "); //$NON-NLS-1$

		textLDAPServerIP=new Text(composite, SWT.BORDER);
		textLDAPServerIP.setLayoutData(new GridData(SWT.FILL,SWT.CENTER,true,false,1,1));
		textLDAPServerIP.setText(LdapConnectionListener.getConnection().getHost());
		textLDAPServerIP.setEnabled(false);
		
		//LDAP DN
		lblLDAPDN = new Label(composite, SWT.NONE);
		lblLDAPDN.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1));
		lblLDAPDN.setText("LDAP DN"); //$NON-NLS-1$

		textLDAPDN=new Text(composite, SWT.BORDER);
		textLDAPDN.setLayoutData(new GridData(SWT.FILL,SWT.CENTER,true,false,1,1));
		textLDAPDN.setText(LdapConnectionListener.getConnection().getConnectionParameter().getExtendedProperty("ldapbrowser.baseDn"));
		textLDAPDN.setEnabled(false);
		
		//LDAP Admin DN
		lblLDAPAdminDN = new Label(composite, SWT.NONE);
		lblLDAPAdminDN.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1));
		lblLDAPAdminDN.setText("LDAP Admin DN"); //$NON-NLS-1$

		textLDAPAdminDN=new Text(composite, SWT.BORDER);
		textLDAPAdminDN.setLayoutData(new GridData(SWT.FILL,SWT.CENTER,true,false,1,1));
		textLDAPAdminDN.setText(UserSettings.USER_DN);
		textLDAPAdminDN.setEnabled(false);
		
		//LDAP Admin Password
		lblLDAPAdminPassword = new Label(composite, SWT.NONE);
		lblLDAPAdminPassword.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1));
		lblLDAPAdminPassword.setText("LDAP Admin Password"); //$NON-NLS-1$

		textLDAPAdminPassword=new Text(composite, SWT.BORDER| SWT.PASSWORD);
		textLDAPAdminPassword.setLayoutData(new GridData(SWT.FILL,SWT.CENTER,true,false,1,1));
		textLDAPAdminPassword.setText(UserSettings.USER_PASSWORD);
		textLDAPAdminPassword.setEnabled(false);
		
		//LDAP Version
		lblLDAPVersion = new Label(composite, SWT.NONE);
		lblLDAPVersion.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1));
		lblLDAPVersion.setText("LDAP Version"); //$NON-NLS-1$

		textLDAPVersion=new Text(composite, SWT.BORDER);
		textLDAPVersion.setLayoutData(new GridData(SWT.FILL,SWT.CENTER,true,false,1,1));
		textLDAPVersion.setText("3");
		
		return composite;
	}

	@Override
	public void validateBeforeExecution() throws ValidationException {
		if(LdapUtils.getInstance().isAdmin(UserSettings.USER_DN) == false) {
			MessageDialog.openWarning(shell, "Admin Yetkisi", "Bu işlemi yapabilmek için admin yetkisine sahip olmalısınız!");
			throw new ValidationException("Bu işlemi yapabilmek için admin yetkisine sahip olmalısınız!");
		}
	}
	
	@Override
	public Map<String, Object> getParameterMap() {
		Map<String, Object> params= new HashMap<>();
		params.put("server-address", LdapConnectionListener.getConnection().getHost());
		params.put("dn", LdapConnectionListener.getConnection().getConnectionParameter().getExtendedProperty("ldapbrowser.baseDn"));
		params.put("admin-dn", UserSettings.USER_DN);
		params.put("admin-password", UserSettings.USER_PASSWORD);
		params.put("version", textLDAPVersion.getText());
		return params;
	}

	@Override
	public String getCommandId() {
		// TODO command id which is used to match tasks with ICommand class in the corresponding Lider plugin
		return "execute_ldap_login";
	}

	@Override
	public String getPluginName() {
		return LDAPLoginConstants.PLUGIN_NAME;
	}

	@Override
	public String getPluginVersion() {
		return LDAPLoginConstants.PLUGIN_VERSION;
	}
	
}
