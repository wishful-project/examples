#include "graphics/qt/realplot/Realplot.h"
#include "deque"

class Realplot;

class QtPlot_xy {
    Realplot *plot_handler;
    std::deque<double> array_exported_to_qt;
    unsigned int max_x;
    unsigned int refresh_rate;
    unsigned int num_samples;

public:
    QtPlot_xy(std::string title = "", std::string x_label = "", std::string y_label = "", unsigned int x_size = 10000, float _refresh_buffer = 0.1);
    void push_back_no_refresh(double val);
    void refresh();
    void push_sample(double val);
    unsigned int get_samples_in_buffer();
    void setXAxisScale(double xMin, double xMax);
    void setYAxisScale(double yMin, double yMax);
    void setXAxisRange(double xMin, double xMax);
};

