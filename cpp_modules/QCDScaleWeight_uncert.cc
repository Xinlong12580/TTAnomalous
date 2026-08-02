// The method implemented here doesn't follow the GEN recipe strictly. You may want to read the GEN recipe or contact the GEN convener if you decide to use this module.
class QCDScaleWeight_uncert{
public:
    QCDScaleWeight_uncert(){}

    ~QCDScaleWeight_uncert(){}

    std::vector<float> eval(RVec<float> LHEScaleWeight) {
        
        LHEScaleWeight.erase(LHEScaleWeight.begin() + 5);
        LHEScaleWeight.erase(LHEScaleWeight.begin() + 7);
        auto uncert = std::minmax_element(LHEScaleWeight.begin(), LHEScaleWeight.end());
        std::vector<float> v = {
            *uncert.second,
            *uncert.first
        };

        return v;
    }
};
