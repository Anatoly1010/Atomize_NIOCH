import atomize.general_modules.general_functions as general
import atomize.device_modules.Mikran_Q_band_MW_bridge as mwBridge

mw = mwBridge.Mikran_Q_band_MW_bridge()

#general.message( mw.mw_bridge_name() )

mw.mw_bridge_open()

#general.message( mw.mw_bridge_telemetry() )

mw.mw_bridge_synthesizer('6800')
general.message( mw.mw_bridge_synthesizer() )

#mw.mw_bridge_att1_prd('10')
#general.message( mw.mw_bridge_att1_prd() )

#general.message( mw.mw_bridge_att_pin('30') )
#general.message( mw.mw_bridge_att_pin() )

#general.message( mw.mw_bridge_att_prm('3') )
#general.message( mw.mw_bridge_att_prm() )

#general.message( mw.mw_bridge_att2_prm('0') )
#general.message( mw.mw_bridge_att2_prm() )

#general.message( mw.mw_bridge_cut_off('105') )
#general.message( mw.mw_bridge_cut_off() )

#mw.mw_bridge_rotary_vane(60, mode = 'Limit')

mw.mw_bridge_close()