#include "QtPlot_xy.h"

QtPlot_xy::QtPlot_xy(std::string title, std::string x_label, std::string y_label, unsigned int x_size, float _refresh_buffer) {
    plot_handler = new Realplot();
    plot_handler->setTitle(title);
    plot_handler->setLabels(x_label, y_label);
    max_x = x_size;
    num_samples = 0;
    array_exported_to_qt.assign(max_x,0);
    refresh_rate = _refresh_buffer * max_x;
}

void QtPlot_xy::push_back_no_refresh(double val) {
    array_exported_to_qt.push_back(val);
    num_samples++;
    if(array_exported_to_qt.size() > max_x)
        array_exported_to_qt.pop_front();
}

void QtPlot_xy::refresh() {
    plot_handler->setNewData(array_exported_to_qt.begin(), array_exported_to_qt.end());
}

void QtPlot_xy::push_sample(double val) {
    push_back_no_refresh(val);
    if(refresh_rate <= num_samples) {
        num_samples = 0;
        refresh();
    }
}

unsigned int QtPlot_xy::get_samples_in_buffer() {
    return num_samples;
}

void QtPlot_xy::setXAxisScale(double xMin, double xMax) {
    plot_handler->setXAxisScale(xMin, xMax);
}

void QtPlot_xy::setYAxisScale(double yMin, double yMax) {
    plot_handler->setYAxisScale(yMin, yMax);
}

void QtPlot_xy::setXAxisRange(double xMin, double xMax) {
    plot_handler->setXAxisRange(xMin, xMax);
}
