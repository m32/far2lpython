	virtual void ResizeDialog(DLGHANDLE hdlg, const CalcCoord & dims)
	{
		Info->SendDlgMessage(hdlg, DM_RESIZEDIALOG, 0, (LONG_PTR)&dims);
	}
	virtual void GetDlgRect(DLGHANDLE hdlg, CalcRect *rect)
	{
		Info->SendDlgMessage(hdlg, DM_GETDLGRECT, 0, (LONG_PTR)rect);
	}
	virtual void GetDlgItemShort(DLGHANDLE hdlg, int id, FarDialogItem *item)
	{
		Info->SendDlgMessage(hdlg, DM_GETDLGITEMSHORT, id, (LONG_PTR)item);
	}
	virtual void SetDlgItemShort(DLGHANDLE hdlg, int id, const FarDialogItem & item)
	{
		Info->SendDlgMessage(hdlg, DM_SETDLGITEMSHORT, id, (LONG_PTR)&item);
	}
	virtual void SetItemPosition(DLGHANDLE hdlg, int id, const CalcRect & rect)
	{
		Info->SendDlgMessage(hdlg, DM_SETITEMPOSITION, id, (LONG_PTR)&rect);
	}
	virtual void EditChange(DLGHANDLE hdlg, int id, const FarDialogItem & item)
	{
		Info->SendDlgMessage(hdlg, DN_EDITCHANGE, id, (LONG_PTR)&item);
	}
	virtual void SetSelection(DLGHANDLE hdlg, int id, const EditorSelect & sel)
	{
		Info->SendDlgMessage(hdlg, DM_SETSELECTION, id, (LONG_PTR)&sel);
	}
	virtual void SetCursorPos(DLGHANDLE hdlg, int id, const CalcCoord & pos)
	{
		Info->SendDlgMessage(hdlg, DM_SETCURSORPOS, id, (LONG_PTR)&pos);
	}
	virtual void AddHistory(DLGHANDLE hdlg, int id, const std::wstring & str)
	{
		Info->SendDlgMessage(hdlg, DM_ADDHISTORY, id, (LONG_PTR)str.c_str());
	}
	virtual bool IsChecked(DLGHANDLE hdlg, int id)
	{
		return ((int)Info->SendDlgMessage(hdlg, DM_GETCHECK, id, 0) == BSTATE_CHECKED);
	}
