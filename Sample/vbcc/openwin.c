/* For license, please see gpl-3.0.txt */
#include <exec/types.h>
#include <intuition/intuition.h>
#include <clib/exec_protos.h>
#include <clib/intuition_protos.h>
#include <stdlib.h>

#define INTUITION_REV 0
#define MILLION 1000000

struct Library *IntuitionBase;

#include "test.h"

int main(int argc, char **argv)
{
  struct NewWindow NewWindow;
  struct Window *Window;
  LONG i;
  UWORD *imdata_chip;

  IntuitionBase = (struct Library *) OpenLibrary("intuition.library", INTUITION_REV);
  if (IntuitionBase == NULL) exit(FALSE);

  NewWindow.LeftEdge = 0;
  NewWindow.TopEdge = 0;
  NewWindow.Width = 340;
  NewWindow.Height = 240;
  NewWindow.DetailPen = 0;
  NewWindow.BlockPen = 1;
  NewWindow.Title = "A Simple Window";
  NewWindow.Flags = WINDOWCLOSE | SMART_REFRESH | ACTIVATE |
    WINDOWSIZING | WINDOWDRAG | WINDOWDEPTH | NOCAREREFRESH;
  NewWindow.IDCMPFlags = CLOSEWINDOW;
  NewWindow.Type = WBENCHSCREEN;
  NewWindow.FirstGadget = NULL;
  NewWindow.CheckMark = NULL;
  NewWindow.Screen = NULL;
  NewWindow.BitMap = NULL;
  NewWindow.MinWidth = 0;
  NewWindow.MinHeight = 0;
  NewWindow.MaxWidth = 0;
  NewWindow.MaxHeight = 0;

  if ((Window = (struct Window *) OpenWindow(&NewWindow)) == NULL) {
    exit(FALSE);
  }
  imdata_chip = AllocMem(sizeof(UWORD) * sizeof(imdata), MEMF_CHIP);
  CopyMem(imdata, imdata_chip, sizeof(UWORD) * sizeof(imdata));
  image.ImageData = imdata_chip;
  
  DrawImage(Window->RPort, &image, 10, 10);
  Wait(1 << Window->UserPort->mp_SigBit);
  FreeMem(imdata_chip, sizeof(UWORD) * sizeof(imdata));
  CloseWindow(Window);
  CloseLibrary(IntuitionBase);
  return 0;
}
