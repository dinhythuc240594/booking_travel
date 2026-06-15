USE `BookingTravel`;

ALTER TABLE `bookings` 
    ADD COLUMN persons INT NULL AFTER check_out_date,
    ADD COLUMN adults INT NULL AFTER persons,
    ADD COLUMN children INT NULL AFTER adults;