#ifndef FEGUIPARAMS_H
#define FEGUIPARAMS_H

struct FEGuiParams
{
  double minFreq;
  double maxFreq;
  double stepFreq;
  bool knobFreq;

  double minBW;
  double maxBW;
  double stepBW;
  bool knobBW;

  double minGain;
  double maxGain;
  double stepGain;
  bool knobGain;

  double min_sync_margin_tx;
  double max_sync_margin_tx;
  double step_sync_margin_tx;
  bool knobMargin;
};

#endif // FEGUIPARAMS_H
